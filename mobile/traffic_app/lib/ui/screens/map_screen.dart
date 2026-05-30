import 'dart:async';
import 'dart:ui' as ui;
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;
import 'package:permission_handler/permission_handler.dart';

import '../../services/api_client.dart';
import '../../services/google_maps_service.dart';
import '../../models/models.dart';
import 'package:traffic_app/core/common.dart';
import '../../core/theme_notifier.dart';
import '../../core/map_styles.dart';

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
  String _trafficLevel = 'Бос';
  String? _weatherDesc;
  double? _temp;
  
  // Vehicles logic
  List<MapVehicle> _vehicles = [];
  Timer? _vehiclesTimer;
  
  // Custom Icons
  gmaps.BitmapDescriptor? _carIcon;
  gmaps.BitmapDescriptor? _busIcon;
  
  // Events & Alerts
  List<Map<String, dynamic>> _userEvents = [];
  gmaps.BitmapDescriptor? _eventAccidentIcon;
  gmaps.BitmapDescriptor? _eventRepairIcon;
  gmaps.BitmapDescriptor? _eventCameraIcon;
  bool _alertShown = false;

  /// Координаты после нажатия «Моё местоположение» — показываем маркер.
  gmaps.LatLng? _myLocation;

  @override
  void initState() {
    super.initState();
    _load();
    _startVehiclesTimer();
    _initIcons();
    ThemeNotifier().addListener(_updateMapStyle);
  }

  Future<void> _initIcons() async {
    _carIcon = await _getMarkerBitmap(80, isBus: false);
    _busIcon = await _getMarkerBitmap(90, isBus: true);
    _eventAccidentIcon = await _getEventMarkerBitmap('💥', Colors.red);
    _eventRepairIcon = await _getEventMarkerBitmap('🚧', Colors.orange);
    _eventCameraIcon = await _getEventMarkerBitmap('📸', Colors.blueGrey);
    if (mounted) setState(() {});
  }

  Future<gmaps.BitmapDescriptor> _getEventMarkerBitmap(String emoji, Color bgColor) async {
    final ui.PictureRecorder pictureRecorder = ui.PictureRecorder();
    final Canvas canvas = Canvas(pictureRecorder);
    const double size = 90;
    const double radius = size / 2;
    
    // Shadow
    final Paint shadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.3)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
    canvas.drawCircle(const Offset(radius, radius + 4), radius - 6, shadowPaint);

    // Background circle
    final Paint paint = Paint()..color = bgColor;
    canvas.drawCircle(const Offset(radius, radius), radius - 6, paint);

    // Border
    final Paint borderPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4;
    canvas.drawCircle(const Offset(radius, radius), radius - 6, borderPaint);

    // Emoji
    TextPainter textPainter = TextPainter(textDirection: TextDirection.ltr);
    textPainter.text = TextSpan(
      text: emoji,
      style: const TextStyle(fontSize: 40),
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(radius - textPainter.width / 2, radius - textPainter.height / 2),
    );

    final ui.Image img = await pictureRecorder.endRecording().toImage(size.toInt(), size.toInt());
    final ByteData? data = await img.toByteData(format: ui.ImageByteFormat.png);
    return gmaps.BitmapDescriptor.fromBytes(data!.buffer.asUint8List());
  }

  Future<gmaps.BitmapDescriptor> _getMarkerBitmap(int size, {required bool isBus}) async {
    final ui.PictureRecorder pictureRecorder = ui.PictureRecorder();
    final Canvas canvas = Canvas(pictureRecorder);
    
    final double radius = size / 2;
    
    // Shadow
    final Paint shadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.3)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    canvas.drawCircle(Offset(radius, radius + 4), radius - 4, shadowPaint);

    // Background circle
    final Paint paint = Paint()..color = isBus ? const Color(0xFFF97316) : const Color(0xFF8B5CF6);
    canvas.drawCircle(Offset(radius, radius), radius - 4, paint);

    // Border
    final Paint borderPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    canvas.drawCircle(Offset(radius, radius), radius - 4, borderPaint);

    // Icon (TextPainter with MaterialIcons font)
    TextPainter textPainter = TextPainter(textDirection: TextDirection.ltr);
    textPainter.text = TextSpan(
      text: String.fromCharCode(isBus ? Icons.directions_bus.codePoint : Icons.directions_car_rounded.codePoint),
      style: TextStyle(
        fontSize: size * 0.55,
        fontFamily: Icons.directions_bus.fontFamily,
        package: Icons.directions_bus.fontPackage,
        color: Colors.white,
      ),
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(radius - textPainter.width / 2, radius - textPainter.height / 2),
    );

    final ui.Image img = await pictureRecorder.endRecording().toImage(size, size);
    final ByteData? data = await img.toByteData(format: ui.ImageByteFormat.png);
    return gmaps.BitmapDescriptor.fromBytes(data!.buffer.asUint8List());
  }

  @override
  void dispose() {
    _vehiclesTimer?.cancel();
    ThemeNotifier().removeListener(_updateMapStyle);
    super.dispose();
  }

  void _startVehiclesTimer() {
    _fetchVehicles();
    _fetchEvents();
    _vehiclesTimer = Timer.periodic(const Duration(seconds: 3), (_) {
      _fetchVehicles();
      _fetchEvents();
    });
  }

  Future<void> _fetchVehicles() async {
    try {
      final v = await api.getVehicles();
      if (mounted) {
        setState(() => _vehicles = v);
      }
    } catch (_) {}
  }

  Future<void> _fetchEvents() async {
    try {
      final events = await api.getEvents();
      if (mounted) {
        setState(() => _userEvents = events);
      }
    } catch (_) {}
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
      String level = 'Бос';
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
        
        if (!_alertShown) {
          _alertShown = true;
          _checkSmartAlert();
        }
      }
    } catch (_) {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _checkSmartAlert() async {
    final alert = await api.getSmartAlert();
    if (alert != null && alert['has_alert'] == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(alert['title'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 4),
              Text(alert['body'], style: const TextStyle(fontSize: 14)),
            ],
          ),
          backgroundColor: alert['title'].toString().contains('🟢') ? Colors.green.shade800 : Colors.red.shade800,
          behavior: SnackBarBehavior.floating,
          margin: EdgeInsets.only(bottom: MediaQuery.of(context).size.height - 180, left: 16, right: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          duration: const Duration(seconds: 6),
        ),
      );
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
          content: Text('Орналасқан жер картада белгіленген'),
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
                label: const Text('Маршрут құру'),
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
        infoWindow: const gmaps.InfoWindow(title: 'Сіз осындасыз'),
      ));
    }
    
    // Add vehicles
    for (final v in _vehicles) {
      final isBus = v.type == 'bus';
      out.add(gmaps.Marker(
        markerId: gmaps.MarkerId('vehicle_${v.id}'),
        position: gmaps.LatLng(v.lat, v.lon),
        icon: isBus ? (_busIcon ?? gmaps.BitmapDescriptor.defaultMarker) : (_carIcon ?? gmaps.BitmapDescriptor.defaultMarker),
        anchor: const Offset(0.5, 0.5), // Center the icon
        infoWindow: gmaps.InfoWindow(
          title: isBus ? '🚌 Автобус' : '🚗 Көлік',
          snippet: v.routeName,
        ),
      ));
    }
    
    // Add user events
    for (final e in _userEvents) {
      gmaps.BitmapDescriptor? icon;
      String title = '';
      if (e['event_type'] == 'accident') {
        icon = _eventAccidentIcon;
        title = '💥 ДТП (Жол апаты)';
      } else if (e['event_type'] == 'repair') {
        icon = _eventRepairIcon;
        title = '🚧 Ремонт (Жол жөндеу)';
      } else if (e['event_type'] == 'camera') {
        icon = _eventCameraIcon;
        title = '📸 Камера';
      }
      out.add(gmaps.Marker(
        markerId: gmaps.MarkerId('event_${e['id']}'),
        position: gmaps.LatLng(e['lat'], e['lng']),
        icon: icon ?? gmaps.BitmapDescriptor.defaultMarker,
        anchor: const Offset(0.5, 0.5),
        infoWindow: gmaps.InfoWindow(title: title),
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
                        Text('Профильге өту', style: TextStyle(color: Colors.white54, fontSize: 14)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const Divider(color: Colors.white10),
            _drawerItem(Icons.map_outlined, 'Картаны жүктеу', () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Скачивание оффлайн карты началось...')),
              );
            }),
            _drawerItem(Icons.directions_walk_rounded, 'Жол іздеу', () {
              Navigator.pop(context);
              globalTabIndex.value = 1; // Переключаемся на Навигатор
            }),
            _drawerItem(Icons.share_location_outlined, 'Геопозициямен бөлісу', () {
              Navigator.pop(context);
              globalTabIndex.value = 3; // Вкладка 'Достар', если она там
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
            _drawerItem(Icons.settings_outlined, 'Баптаулар', () {
              Navigator.pop(context);
              globalTabIndex.value = 4; // Вкладка 'Тағы' (профиль/настройки)
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
              onLongPress: _onMapLongPress,
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
                        Expanded(child: _horizonChip(0, 'Қазір')),
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
                    Text('Жүктелуде...', style: TextStyle(fontSize: 13, color: AppColors.textSecondary)),
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
                      'Іздеу',
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

  void _onMapLongPress(gmaps.LatLng pos) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Theme.of(context).scaffoldBackgroundColor,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40, height: 4,
                margin: const EdgeInsets.only(bottom: 20),
                decoration: BoxDecoration(color: Colors.grey.withOpacity(0.3), borderRadius: BorderRadius.circular(2)),
              ),
            ),
            const Text('Жол оқиғасын хабарлау', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('Картадағы басқа жүргізушілерге көмектесіңіз', style: TextStyle(fontSize: 14, color: Colors.grey)),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _eventButton(ctx, '💥', 'ДТП', 'accident', pos),
                _eventButton(ctx, '🚧', 'Ремонт', 'repair', pos),
                _eventButton(ctx, '📸', 'Камера', 'camera', pos),
              ],
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _eventButton(BuildContext ctx, String emoji, String label, String type, gmaps.LatLng pos) {
    return InkWell(
      onTap: () async {
        Navigator.pop(ctx);
        final success = await api.postEvent(type, pos.latitude, pos.longitude);
        if (success && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Оқиға сәтті қосылды!')));
          _fetchEvents(); // update immediately
        }
      },
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              shape: BoxShape.circle,
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8)],
            ),
            child: Text(emoji, style: const TextStyle(fontSize: 32)),
          ),
          const SizedBox(height: 8),
          Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
