import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;
import 'package:permission_handler/permission_handler.dart';

import 'api.dart';
import 'models.dart';
import 'package:traffic_app/common.dart';

/// Центр карты — Астана
final gmaps.LatLng _kAstanaCenter = gmaps.LatLng(51.1694, 71.4491);

class MapScreen extends StatefulWidget {
  final bool showFriendsOnMap;
  final void Function(bool)? onShowFriendsChanged;

  const MapScreen({super.key, this.showFriendsOnMap = false, this.onShowFriendsChanged});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final api = ApiClient();

  int horizon = 0;
  bool loading = true;
  List<RoadSegment> segments = [];
  bool _loadingPlace = false;
  gmaps.GoogleMapController? _mapController;
  /// Координаты после нажатия «Моё местоположение» — показываем маркер.
  gmaps.LatLng? _myLocation;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => loading = true);
    try {
      final items = await api.getRoadSegments(horizon);
      final filtered = items.where((s) => s.points.length >= 2).toList();
      if (mounted) {
        setState(() {
          segments = filtered;
          loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _goToMyLocation() async {
    if (!mounted) return;
    final enabled = await Geolocator.isLocationServiceEnabled();
    if (!enabled) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Включите геолокацию в настройках устройства'),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }
    final status = await Permission.location.request();
    if (!status.isGranted) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Нужен доступ к местоположению для показа точки на карте'),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
      return;
    }
    try {
      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.medium,
        timeLimit: const Duration(seconds: 10),
      );
      if (!mounted) return;
      final latLng = gmaps.LatLng(pos.latitude, pos.longitude);
      setState(() => _myLocation = latLng);
      _mapController?.animateCamera(gmaps.CameraUpdate.newLatLng(latLng));
      _mapController?.animateCamera(gmaps.CameraUpdate.zoomTo(15));
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Местоположение отмечено на карте'),
          duration: Duration(seconds: 2),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Не удалось получить координаты: $e'),
            backgroundColor: Colors.red.shade700,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  void _onMapTap(gmaps.LatLng position) async {
    if (_loadingPlace) return;
    setState(() => _loadingPlace = true);
    try {
      final placeId = await getNearbyPlaceId(position.latitude, position.longitude);
      if (!mounted) return;
      setState(() => _loadingPlace = false);
      if (placeId != null) {
        final place = await getPlaceDetailsFull(placeId);
        if (!mounted) return;
        _showPlaceCard(place);
      } else {
        final address = await getAddressForLatLng(position.latitude, position.longitude);
        if (!mounted) return;
        ScaffoldMessenger.of(context).clearSnackBars();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(address),
            duration: const Duration(seconds: 5),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (_) {
      if (mounted) setState(() => _loadingPlace = false);
    }
  }

  void _showPlaceCard(PlaceDetailsFull place) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.3,
        maxChildSize: 0.92,
        builder: (_, scrollController) => Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.divider,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                place.name,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
              if (place.rating != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.star_rounded, color: Color(0xFFEAB308), size: 22),
                    const SizedBox(width: 6),
                    Text(
                      '${place.rating!.toStringAsFixed(1)}${place.userRatingsTotal != null ? ' (${place.userRatingsTotal} отзывов)' : ''}',
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ],
              if (place.photoUrls.isNotEmpty) ...[
                const SizedBox(height: 12),
                SizedBox(
                  height: 180,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: place.photoUrls.length,
                    itemBuilder: (_, i) => Padding(
                      padding: EdgeInsets.only(right: i < place.photoUrls.length - 1 ? 10 : 0),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.network(
                          place.photoUrls[i],
                          width: 280,
                          height: 180,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Container(
                            width: 280,
                            height: 180,
                            color: AppColors.surfaceVariant,
                            child: const Icon(Icons.image_not_supported, size: 48),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
              if (place.openingHoursText != null || place.openNow != null) ...[
                const SizedBox(height: 14),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.schedule_rounded, size: 20, color: AppColors.primary),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (place.openNow != null)
                            Text(
                              place.openNow! ? 'Открыто' : 'Закрыто',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                color: place.openNow! ? const Color(0xFF22C55E) : Colors.red,
                                fontSize: 14,
                              ),
                            ),
                          if (place.openingHoursText != null && place.openingHoursText!.isNotEmpty)
                            Text(
                              place.openingHoursText!,
                              style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
              if (place.phone != null && place.phone!.isNotEmpty) ...[
                const SizedBox(height: 10),
                _placeRow(Icons.phone_rounded, place.phone!, () {}),
              ],
              if (place.website != null && place.website!.isNotEmpty) ...[
                const SizedBox(height: 8),
                _placeRow(Icons.language_rounded, place.website!, () {}),
              ],
              const SizedBox(height: 10),
              _placeRow(Icons.location_on_rounded, place.address, () {}),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.traffic_rounded, size: 18, color: AppColors.textSecondary),
                  const SizedBox(width: 8),
                  Text(
                    'Загруженность: обычно людно в часы пик',
                    style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              FilledButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  // Можно передать место в Навигатор через callback или глобальное состояние
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Построить маршрут до «${place.name}» — откройте вклад Навигатор и введите адрес'),
                      duration: const Duration(seconds: 4),
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                },
                icon: const Icon(Icons.route_rounded, size: 22),
                label: const Text('Построить маршрут'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _placeRow(IconData icon, String text, VoidCallback onTap) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: AppColors.primary),
        const SizedBox(width: 10),
        Expanded(
          child: GestureDetector(
            onTap: onTap,
            child: Text(
              text,
              style: const TextStyle(fontSize: 14, color: AppColors.textPrimary),
            ),
          ),
        ),
      ],
    );
  }

  Set<gmaps.Polyline> _buildPolylines() {
    final Set<gmaps.Polyline> out = {};
    int idx = 0;
    for (final s in segments) {
      if (s.points.length < 2) continue;
      final points = s.points
          .map((p) => gmaps.LatLng(p.latitude, p.longitude))
          .toList();
      final color = colorByValue(s.value);
      out.add(gmaps.Polyline(
        polylineId: gmaps.PolylineId('seg_shadow_$idx'),
        points: points,
        color: Colors.black.withOpacity(0.2),
        width: 14,
      ));
      out.add(gmaps.Polyline(
        polylineId: gmaps.PolylineId('seg_$idx'),
        points: points,
        color: color,
        width: 10,
      ));
      idx++;
    }
    return out;
  }

  Set<gmaps.Marker> _buildMarkers() {
    final Set<gmaps.Marker> out = {};
    if (_myLocation != null) {
      out.add(gmaps.Marker(
        markerId: const gmaps.MarkerId('my_location'),
        position: _myLocation!,
        icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(gmaps.BitmapDescriptor.hueAzure),
        infoWindow: const gmaps.InfoWindow(title: 'Вы здесь'),
      ));
    }
    return out;
  }

  Widget _horizonChip(int value, String label) {
    final selected = horizon == value;
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () {
          setState(() => horizon = value);
          _load();
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: selected ? AppColors.primary : Colors.white,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: selected ? AppColors.primary : AppColors.divider.withOpacity(0.7),
              width: selected ? 2 : 1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(selected ? 0.08 : 0.04),
                blurRadius: selected ? 12 : 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 15,
                color: selected ? Colors.white : AppColors.textPrimary,
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: whiteAppBar('Карта трафика'),
      body: Stack(
        children: [
          Column(
            children: [
              RefreshIndicator(
                onRefresh: _load,
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
                    child: Row(
                      children: [
                        Expanded(child: _horizonChip(0, 'Сейчас')),
                        const SizedBox(width: 10),
                        Expanded(child: _horizonChip(30, '30')),
                        const SizedBox(width: 10),
                        Expanded(child: _horizonChip(60, '60')),
                      ],
                    ),
                  ),
                ),
              ),
              if (_loadingPlace)
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  child: Row(
                    children: [
                      SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
                      SizedBox(width: 8),
                      Text('Загрузка места...', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                    ],
                  ),
                ),
              Expanded(
                child: gmaps.GoogleMap(
                  initialCameraPosition: gmaps.CameraPosition(
                    target: _kAstanaCenter,
                    zoom: 12,
                  ),
                  onMapCreated: (c) => _mapController = c,
                  onTap: _onMapTap,
                  polylines: _buildPolylines(),
                  markers: _buildMarkers(),
                  mapToolbarEnabled: true,
                  myLocationButtonEnabled: false,
                  zoomControlsEnabled: false,
                  trafficEnabled: true,
                ),
              ),
            ],
          ),
          Positioned(
            right: 16,
            bottom: 24,
            child: GestureDetector(
              onTap: () => _goToMyLocation(),
              behavior: HitTestBehavior.opaque,
              child: Material(
                elevation: 4,
                borderRadius: BorderRadius.circular(14),
                child: Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: AppColors.divider.withOpacity(0.5)),
                  ),
                  child: const Icon(Icons.my_location_rounded, color: AppColors.primary, size: 28),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
