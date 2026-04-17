import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;
import 'package:permission_handler/permission_handler.dart';

import 'api.dart';
import 'models.dart';
import 'package:traffic_app/common.dart';
import 'theme_notifier.dart';
import 'map_styles.dart';
import 'friends_screen.dart';

/// Центр карты — Астана
final gmaps.LatLng _kAstanaCenter = gmaps.LatLng(51.1694, 71.4491);

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
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  int horizon = 0;
  bool loading = true;
  List<RoadSegment> segments = [];
  bool _loadingPlace = false;
  gmaps.GoogleMapController? _mapController;
  int _overallPoints = 0;
  String _trafficLevel = 'Свободно';
  String? _weatherDesc;
  double? _temp;
  List<Friend> _friends = [];
  
  // Smart Parking
  bool _showParking = false;
  List<dynamic> _parkings = [];

  /// Координаты после нажатия «Моё местоположение» — показываем маркер.
  gmaps.LatLng? _myLocation;

  // Custom Modern Markers
  gmaps.BitmapDescriptor? _parkingIcon;
  gmaps.BitmapDescriptor? _myIcon;
  final Map<String, gmaps.BitmapDescriptor> _friendIcons = {};

  @override
  void initState() {
    super.initState();
    _initIcons();
    _load();
    _initLocation();
    ThemeNotifier().addListener(_updateMapStyle);
  }

  Future<void> _initIcons() async {
    _parkingIcon = await createModernMarker(text: 'P', bgColor: const Color(0xFF2563EB), isSquare: true);
    _myIcon = await createModernMarker(text: 'Я', bgColor: AppColors.primary);
    if (mounted) setState(() {});
  }

  Future<void> _initLocation() async {
    final enabled = await Geolocator.isLocationServiceEnabled();
    if (!enabled) return;
    
    var status = await Permission.location.status;
    if (status.isGranted) {
      try {
        final pos = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.medium,
          timeLimit: const Duration(seconds: 5),
        );
        api.updateMyLocation(pos.latitude, pos.longitude);
        if (mounted) {
          setState(() {
            _myLocation = gmaps.LatLng(pos.latitude, pos.longitude);
          });
        }
      } catch (_) {}
    }
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
      final segs = await api.getRoadSegments(horizon);
      final metrics = await api.getTrafficMetrics();
      final weather = await api.getWeatherData();
      final fList = await api.getFriends();
      final parkingData = await api.getParkings(horizon);

      if (mounted) {
        for (var f in fList) {
          if (!_friendIcons.containsKey(f.id)) {
            _friendIcons[f.id] = await createModernMarker(
              text: f.name.isNotEmpty ? f.name[0].toUpperCase() : 'F',
              bgColor: const Color(0xFF10B981),
            );
          }
        }
        setState(() {
          segments = segs.where((s) => s.points.length >= 2).toList();
          _overallPoints = metrics.globalScore;
          _trafficLevel = metrics.level;
          _weatherDesc = weather['description']?.toString();
          _temp = (weather['temp'] as num?)?.toDouble();
          _friends = fList;
          _parkings = parkingData['items'] as List<dynamic>? ?? [];
          loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _goToMyLocation() async {
    if (!mounted) return;
    final status = await Permission.location.request();
    if (!status.isGranted) return;
    try {
      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.medium,
        timeLimit: const Duration(seconds: 10),
      );
      if (!mounted) return;
      final latLng = gmaps.LatLng(pos.latitude, pos.longitude);
      api.updateMyLocation(pos.latitude, pos.longitude);
      setState(() => _myLocation = latLng);
      _mapController?.animateCamera(gmaps.CameraUpdate.newLatLng(latLng));
      _mapController?.animateCamera(gmaps.CameraUpdate.zoomTo(15));
    } catch (_) {}
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
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(address), behavior: SnackBarBehavior.floating));
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
            borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
            children: [
              Center(
                child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey.withOpacity(0.3), borderRadius: BorderRadius.circular(2))),
              ),
              const SizedBox(height: 20),
              Text(place.name, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
              const SizedBox(height: 8),
              if (place.rating != null)
                Row(
                  children: [
                    const Icon(Icons.star_rounded, color: Color(0xFFEAB308), size: 22),
                    const SizedBox(width: 4),
                    Text('${place.rating!.toStringAsFixed(1)} (${place.userRatingsTotal} отзывов)', 
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
                  ],
                ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: () {
                    Navigator.pop(ctx);
                    globalRouteRequest.value = GlobalRouteRequest(
                      destinationName: place.name, destinationLat: place.lat, destinationLng: place.lng);
                    globalTabIndex.value = 1;
                  },
                  icon: const Icon(Icons.route_rounded),
                  label: const Text('Построить маршрут'),
                  style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Set<gmaps.Polyline> _buildPolylines() {
    if (horizon == 0) return {};
    final Set<gmaps.Polyline> out = {};
    int idx = 0;
    for (final s in segments) {
      if (s.points.length < 2) continue;
      out.add(gmaps.Polyline(
        polylineId: gmaps.PolylineId('seg_$idx'),
        points: s.points.map((p) => gmaps.LatLng(p.latitude, p.longitude)).toList(),
        color: colorByValue(s.value),
        width: 6,
        jointType: gmaps.JointType.round,
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
        icon: _myIcon ?? gmaps.BitmapDescriptor.defaultMarker,
      ));
    }
    for (var f in _friends) {
      if (f.lat != null && f.lon != null) {
        out.add(gmaps.Marker(
          markerId: gmaps.MarkerId('friend_${f.id}'),
          position: gmaps.LatLng(f.lat!, f.lon!),
          icon: _friendIcons[f.id] ?? gmaps.BitmapDescriptor.defaultMarker,
        ));
      }
    }
    if (_showParking) {
      for (final p in _parkings) {
        out.add(gmaps.Marker(
          markerId: gmaps.MarkerId('parking_${p['id']}'),
          position: gmaps.LatLng((p['lat'] as num).toDouble(), (p['lng'] as num).toDouble()),
          icon: _parkingIcon ?? gmaps.BitmapDescriptor.defaultMarker,
          infoWindow: gmaps.InfoWindow(title: '🅿️ ${p['name']}', snippet: 'Бос: ${p['available']}'),
        ));
      }
    }
    return out;
  }

  Widget _horizonChip(int value, String label) {
    final selected = horizon == value;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() => horizon = value);
          _load();
        },
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            gradient: selected ? const LinearGradient(colors: [Color(0xFF0D7EA7), Color(0xFF065A82)]) : null,
            color: selected ? null : const Color(0xFF1E2023).withOpacity(0.9),
            borderRadius: BorderRadius.circular(18),
            boxShadow: [if (selected) BoxShadow(color: const Color(0xFF0D7EA7).withOpacity(0.4), blurRadius: 10, offset: const Offset(0, 4))],
          ),
          child: Center(
            child: Text(label, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: selected ? Colors.white : Colors.white70)),
          ),
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

  Widget _buildProfileDrawer() {
    return Drawer(
      backgroundColor: const Color(0xFF1E2023),
      child: SafeArea(
        child: Column(
          children: [
            const Padding(
              padding: EdgeInsets.all(24),
              child: Row(
                children: [
                  CircleAvatar(radius: 28, backgroundImage: NetworkImage('https://ui-avatars.com/api/?name=User&background=0D7EA7&color=fff')),
                  SizedBox(width: 16),
                  Text('Алишер', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
            const Divider(color: Colors.white10),
            _drawerItem(Icons.map_outlined, 'Қазақстан картасы', () => Navigator.pop(context)),
            _drawerItem(Icons.settings_outlined, 'Баптаулар', () => Navigator.pop(context)),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      drawer: _buildProfileDrawer(),
      body: Stack(
        children: [
          // 1. Google Map
          Positioned.fill(
            child: gmaps.GoogleMap(
              initialCameraPosition: gmaps.CameraPosition(target: _kAstanaCenter, zoom: 12),
              onMapCreated: (c) {
                _mapController = c;
                _updateMapStyle();
              },
              onTap: _onMapTap,
              polylines: _buildPolylines(),
              markers: _buildMarkers(),
              myLocationButtonEnabled: false,
              zoomControlsEnabled: false,
              trafficEnabled: true,
              compassEnabled: false,
              mapToolbarEnabled: false, // Remove Google Map's native artifacts
            ),
          ),

          // 2. Top Stats & Horizon
          Positioned(
            top: 0, left: 0, right: 0,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Column(
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Traffic Points
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                          decoration: BoxDecoration(
                            color: _getPointColor(_overallPoints),
                            borderRadius: BorderRadius.circular(18),
                            boxShadow: [BoxShadow(color: _getPointColor(_overallPoints).withOpacity(0.4), blurRadius: 12, offset: const Offset(0, 4))],
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.traffic_rounded, color: Colors.white, size: 22),
                              const SizedBox(width: 8),
                              Text('$_overallPoints', style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w900)),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        // Weather Widget (Improved Glass Design)
                        if (_temp != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                            decoration: BoxDecoration(
                              color: const Color(0xFF1E2023).withOpacity(0.9),
                              borderRadius: BorderRadius.circular(18),
                              boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 10)],
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.wb_cloudy_rounded, color: Colors.blueAccent, size: 22),
                                const SizedBox(width: 10),
                                Column(
                                  mainAxisSize: MainAxisSize.min,
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text('${_temp?.round() ?? '--'}°C', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 16)),
                                    if (_weatherDesc != null)
                                      Text(_weatherDesc!, style: const TextStyle(color: Colors.white54, fontSize: 10, fontWeight: FontWeight.bold)),
                                  ],
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    // Horizon Chips
                    Row(
                      children: [
                        _horizonChip(0, 'Қазір'),
                        const SizedBox(width: 8),
                        _horizonChip(30, '30 мин'),
                        const SizedBox(width: 8),
                        _horizonChip(60, '60 мин'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),

          // 3. Floating Action Buttons
          Positioned(
            right: 16, bottom: 100,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _mapFab(
                  icon: Icons.local_parking_rounded,
                  active: _showParking,
                  onTap: () => setState(() => _showParking = !_showParking),
                ),
                const SizedBox(height: 12),
                _mapFab(
                  icon: Icons.my_location_rounded,
                  onTap: _goToMyLocation,
                ),
              ],
            ),
          ),

          // 4. Modern Bottom Search Bar
          Positioned(
            left: 16, right: 16, bottom: 24,
            child: GestureDetector(
              onTap: () => _scaffoldKey.currentState?.openDrawer(),
              child: Container(
                height: 58,
                decoration: BoxDecoration(
                  color: const Color(0xFF1E2023),
                  borderRadius: BorderRadius.circular(18),
                  boxShadow: const [BoxShadow(color: Colors.black45, blurRadius: 15, offset: Offset(0, 4))],
                ),
                child: Row(
                  children: [
                    const SizedBox(width: 18),
                    const Icon(Icons.search_rounded, color: Colors.white70),
                    const SizedBox(width: 14),
                    const Expanded(child: Text('Іздеу немесе маршрут', style: TextStyle(color: Colors.white54, fontSize: 17, fontWeight: FontWeight.w500))),
                    const VerticalDivider(color: Colors.white10, indent: 16, endIndent: 16),
                    IconButton(icon: const Icon(Icons.menu_rounded, color: Colors.white), onPressed: () => _scaffoldKey.currentState?.openDrawer()),
                    const SizedBox(width: 6),
                  ],
                ),
              ),
            ),
          ),
          
          if (loading) const Center(child: CircularProgressIndicator()),
        ],
      ),
    );
  }

  Widget _mapFab({required IconData icon, bool active = false, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 52, height: 52,
        decoration: BoxDecoration(
          color: active ? const Color(0xFF2563EB) : const Color(0xFF1E2023).withOpacity(0.9),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [BoxShadow(color: Colors.black38, blurRadius: 10, offset: const Offset(0, 4))],
        ),
        child: Icon(icon, color: active ? Colors.white : Colors.white),
      ),
    );
  }

  Color _getPointColor(int points) {
    if (points <= 3) return const Color(0xFF22C55E);
    if (points <= 6) return const Color(0xFFEAB308);
    if (points <= 8) return const Color(0xFFEF4444);
    return const Color(0xFF7F1D1D);
  }
}
