import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;
import 'package:permission_handler/permission_handler.dart';

import 'api.dart';
import 'models.dart';
import 'package:traffic_app/common.dart';
import 'theme_notifier.dart';
import 'map_styles.dart';

/// Центр карты — Астана
const gmaps.LatLng _kAstanaCenter = gmaps.LatLng(51.1694, 71.4491);

class MapScreen extends StatefulWidget {
  final bool showFriendsOnMap;
  final void Function(bool)? onShowFriendsChanged;

  const MapScreen(
      {super.key, this.showFriendsOnMap = false, this.onShowFriendsChanged});

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
  int _overallPoints = 0;
  String _trafficLevel = 'Свободно';
  String? _weatherDesc;
  double? _temp;

  /// Координаты после нажатия «Моё местоположение» — показываем маркер.
  gmaps.LatLng? _myLocation;

  @override
  void initState() {
    super.initState();
    _load();
    ThemeNotifier().addListener(_updateMapStyle);
  }

  @override
  void dispose() {
    ThemeNotifier().removeListener(_updateMapStyle);
    super.dispose();
  }

  void _updateMapStyle() {
    if (_mapController != null) {
      if (ThemeNotifier().isDarkMode) {
        _mapController!.setMapStyle(googleMapsDarkStyle);
      } else {
        _mapController!.setMapStyle(null);
      }
    }
  }

  Future<void> _load() async {
    setState(() => loading = true);
    try {
      // 1. Загружаем реальные сегменты дорог из Supabase
      try {
        final segs = await api.getRoadSegments(horizon);
        segments = segs.where((s) => s.points.length >= 2).toList();
      } catch (_) {}

      // 2. Трафик-балл (реальный, из сегментов)
      int pts = 0;
      try {
        final data = await api.getTrafficMap(horizon);
        pts = (data['overall_points'] as num?)?.toInt() ?? 0;
      } catch (_) {}

      // 3. Детальные метрики
      String level = 'Свободно';
      try {
        final metrics = await api.getTrafficMetrics();
        pts = metrics.globalScore;
        level = metrics.level;
      } catch (_) {}

      // 4. Реальная погода (OpenWeatherMap)
      String? weatherDesc;
      double? temp;
      try {
        final weather = await api.getWeatherData();
        weatherDesc = weather['description']?.toString();
        temp = (weather['temp'] as num?)?.toDouble();
      } catch (_) {}

      if (mounted) {
        setState(() {
          _overallPoints = pts;
          _trafficLevel = level;
          _weatherDesc = weatherDesc;
          _temp = temp;
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
            content:
                Text('Нужен доступ к местоположению для показа точки на карте'),
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
      final placeId =
          await getNearbyPlaceId(position.latitude, position.longitude);
      if (!mounted) return;
      setState(() => _loadingPlace = false);
      if (placeId != null) {
        final place = await getPlaceDetailsFull(placeId);
        if (!mounted) return;
        _showPlaceCard(place);
      } else {
        final address =
            await getAddressForLatLng(position.latitude, position.longitude);
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
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
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
                    const Icon(Icons.star_rounded,
                        color: Color(0xFFEAB308), size: 22),
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
                      padding: EdgeInsets.only(
                          right: i < place.photoUrls.length - 1 ? 10 : 0),
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
                            child:
                                const Icon(Icons.image_not_supported, size: 48),
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
                    const Icon(Icons.schedule_rounded,
                        size: 20, color: AppColors.primary),
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
                                color: place.openNow!
                                    ? const Color(0xFF22C55E)
                                    : Colors.red,
                                fontSize: 14,
                              ),
                            ),
                          if (place.openingHoursText != null &&
                              place.openingHoursText!.isNotEmpty)
                            Text(
                              place.openingHoursText!,
                              style: const TextStyle(
                                  fontSize: 13, color: AppColors.textSecondary),
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
              const Row(
                children: [
                  Icon(Icons.traffic_rounded,
                      size: 18, color: AppColors.textSecondary),
                  SizedBox(width: 8),
                  Text(
                    'Загруженность: обычно людно в часы пик',
                    style:
                        TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              FilledButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  globalRouteRequest.value = GlobalRouteRequest(
                    destinationName: place.name,
                    destinationLat: place.lat,
                    destinationLng: place.lng,
                  );
                  globalTabIndex.value = 1; // Переключаемся на Навигатор
                },
                icon: const Icon(Icons.route_rounded, size: 22),
                label: const Text('Построить маршрут'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
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
              style:
                  const TextStyle(fontSize: 14, color: AppColors.textPrimary),
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
      final points =
          s.points.map((p) => gmaps.LatLng(p.latitude, p.longitude)).toList();
      final color = colorByValue(s.value);
      out.add(gmaps.Polyline(
        polylineId: gmaps.PolylineId('seg_shadow_$idx'),
        points: points,
        color: Colors.black.withValues(alpha: 0.2),
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
        icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(
            gmaps.BitmapDescriptor.hueAzure),
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
            color: selected ? AppColors.primary : Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: selected
                  ? AppColors.primary
                  : Theme.of(context).dividerColor.withValues(alpha: 0.7),
              width: selected ? 2 : 1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: selected ? 0.08 : 0.04),
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
                color: selected ? Colors.white : Theme.of(context).textTheme.bodyMedium?.color,
              ),
            ),
          ),
        ),
      ),
    );
  }

  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  Widget _buildProfileDrawer() {
    return Drawer(
      backgroundColor: const Color(0xFF1E2023),
      shape: const RoundedRectangleBorder(),
      child: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: Theme.of(context).primaryColor,
                    // Используем генератор аватарок с инициалами до подключения настоящего бэкенда авторизации
                    backgroundImage: const NetworkImage('https://ui-avatars.com/api/?name=Алиш1rqp+Сулейменов&background=0D7EA7&color=fff&size=100'),
                  ),
                  const SizedBox(width: 16),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Алиш1rqp Сулейменов', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                        SizedBox(height: 4),
                        Text('Перейти в профиль', style: TextStyle(color: Colors.white54, fontSize: 14)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const Divider(color: Colors.white10),
            _drawerItem(Icons.map_outlined, 'Скачать карту', () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Скачивание оффлайн карты началось...')),
              );
            }),
            _drawerItem(Icons.directions_walk_rounded, 'Поиск проезда', () {
              Navigator.pop(context);
              globalTabIndex.value = 1; // Переключаемся на Навигатор
            }),
            _drawerItem(Icons.share_location_outlined, 'Делиться геопозицией', () {
              Navigator.pop(context);
              globalTabIndex.value = 3; // Вкладка 'Друзья', если она там
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Переход к списку друзей...')),
              );
            }),
            _drawerItem(Icons.bookmark_outline, 'Избранное', () {
              Navigator.pop(context);
              globalTabIndex.value = 1; // Навигатор содержит избранное
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Ваши избранные маршруты находятся в Навигаторе')),
              );
            }),
            _drawerItem(Icons.flag_outlined, 'Гид по городу', () {
              Navigator.pop(context);
              globalTabIndex.value = 2; // AI Советы
            }),
            _drawerItem(Icons.settings_outlined, 'Настройки', () {
              Navigator.pop(context);
              globalTabIndex.value = 4; // Вкладка 'Ещё' (профиль/настройки)
            }),
          ],
        ),
      ),
    );
  }

  Widget _drawerItem(IconData icon, String title, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon, color: Colors.white70),
      title: Text(title, style: const TextStyle(color: Colors.white, fontSize: 16)),
      onTap: onTap,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      drawer: _buildProfileDrawer(),
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: Stack(
        children: [
          // 1. Fullscreen Google Map
          Positioned.fill(
            child: gmaps.GoogleMap(
              initialCameraPosition: const gmaps.CameraPosition(
                target: _kAstanaCenter,
                zoom: 12,
              ),
              onMapCreated: (c) {
                _mapController = c;
                _updateMapStyle();
              },
              onTap: _onMapTap,
              polylines: _buildPolylines(),
              markers: _buildMarkers(),
              mapToolbarEnabled: true,
              myLocationButtonEnabled: false,
              zoomControlsEnabled: false,
              trafficEnabled: true,
            ),
          ),

          // 2. Top Widgets (Traffic Score, Weather, Chips)
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              bottom: false,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Traffic Points (2GIS style)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                          decoration: BoxDecoration(
                            color: _getPointColor(_overallPoints),
                            borderRadius: BorderRadius.circular(16),
                            boxShadow: [
                              BoxShadow(
                                color: _getPointColor(_overallPoints).withValues(alpha: 0.3),
                                blurRadius: 10, offset: const Offset(0, 3)),
                            ],
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.traffic_rounded, color: Colors.white, size: 20),
                              const SizedBox(width: 8),
                              Text(
                                '$_overallPoints',
                                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w800),
                              ),
                              const SizedBox(width: 4),
                              const Text('б.', style: TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.w600)),
                            ],
                          ),
                        ),
                        const SizedBox(width: 10),
                        // Traffic Level Text Container
                        if (_overallPoints > 0)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: BoxDecoration(
                              color: Theme.of(context).cardColor.withValues(alpha: 0.9),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: Theme.of(context).dividerColor),
                            ),
                            child: Text(
                              _trafficLevel,
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: _getPointColor(_overallPoints)),
                            ),
                          ),
                        const Spacer(),
                        // Weather Info (реальные данные OpenWeatherMap)
                        if (_temp != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            decoration: BoxDecoration(
                              color: Theme.of(context).cardColor,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: Theme.of(context).dividerColor.withValues(alpha: 0.5)),
                              boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, 2))],
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.cloud_queue_rounded, color: AppColors.primary, size: 20),
                                const SizedBox(width: 8),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      '${_temp?.round() ?? '--'}°C',
                                      style: TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w700,
                                        color: Theme.of(context).textTheme.bodyMedium?.color,
                                      ),
                                    ),
                                    if (_weatherDesc != null && _weatherDesc!.isNotEmpty)
                                      Text(
                                        _weatherDesc!,
                                        style: TextStyle(
                                          fontSize: 10,
                                          color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.6),
                                        ),
                                      ),
                                  ],
                                ),
                              ],

                            ),
                          ),
                      ],
                    ),
                  ),
                  // Horizon Chips
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                    child: Row(
                      children: [
                        Expanded(child: _horizonChip(0, 'Сейчас')),
                        const SizedBox(width: 8),
                        Expanded(child: _horizonChip(30, '30 мин')),
                        const SizedBox(width: 8),
                        Expanded(child: _horizonChip(60, '60 мин')),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Loading overlay
          if (_loadingPlace)
            Positioned(
              top: MediaQuery.of(context).padding.top + 130,
              left: 16,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 8)],
                ),
                child: const Row(
                  children: [
                    SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                    SizedBox(width: 8),
                    Text('Загрузка...', style: TextStyle(fontSize: 13, color: AppColors.textSecondary)),
                  ],
                ),
              ),
            ),

          // My Location Target Button
          Positioned(
            right: 16,
            bottom: 110,
            child: GestureDetector(
              onTap: () => _goToMyLocation(),
              behavior: HitTestBehavior.opaque,
              child: Material(
                elevation: 4,
                borderRadius: BorderRadius.circular(16),
                child: Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Theme.of(context).dividerColor.withValues(alpha: 0.3)),
                  ),
                  child: const Icon(Icons.my_location_rounded, color: AppColors.primary, size: 26),
                ),
              ),
            ),
          ),

          // 3. Bottom Search Bar (2GIS Style)
          Positioned(
            left: 16,
            right: 16,
            bottom: 24,
            child: Container(
              height: 56,
              decoration: BoxDecoration(
                color: const Color(0xFF2B2D31), // Dark gray search bar as in 2GIS
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [
                  BoxShadow(color: Colors.black38, blurRadius: 10, offset: Offset(0, 4)),
                ],
              ),
              child: Row(
                children: [
                  const SizedBox(width: 16),
                  const Icon(Icons.search_rounded, color: Colors.white70, size: 24),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'Поиск',
                      style: TextStyle(color: Colors.white54, fontSize: 17, fontWeight: FontWeight.w500),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.mic_none_rounded, color: Colors.white70),
                    onPressed: () {},
                  ),
                  Container(width: 1, height: 24, color: Colors.white24),
                  IconButton(
                    icon: const Icon(Icons.menu_rounded, color: Colors.white),
                    onPressed: () => _scaffoldKey.currentState?.openDrawer(),
                  ),
                  const SizedBox(width: 4),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getPointColor(int points) {
    if (points <= 3) return Colors.green;
    if (points <= 6) return Colors.orange;
    if (points <= 8) return Colors.red;
    return const Color(0xFF7F1D1D); // Dark red
  }
}
