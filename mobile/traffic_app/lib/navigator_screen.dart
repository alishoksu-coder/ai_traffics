import 'dart:async';
import 'dart:ui' as dart_ui;

import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;
import 'package:latlong2/latlong.dart';

import 'api.dart';
import 'models.dart';
import 'package:traffic_app/common.dart';
import 'theme_notifier.dart';
import 'map_styles.dart';

class NavigatorScreen extends StatefulWidget {
  const NavigatorScreen({super.key});

  @override
  State<NavigatorScreen> createState() => _NavigatorScreenState();
}

/// Центр карты — Астана
final gmaps.LatLng _kAstanaCenter = gmaps.LatLng(51.1694, 71.4491);

class _NavigatorScreenState extends State<NavigatorScreen> {
  gmaps.GoogleMapController? _mapController;

  final TextEditingController _fromController = TextEditingController();
  final TextEditingController _toController = TextEditingController();
  final FocusNode _fromFocus = FocusNode();
  final FocusNode _toFocus = FocusNode();

  bool loading = false;
  String? error;

  /// Точка A (откуда) и B (куда).
  LatLng? a;
  LatLng? b;

  /// Режим: пешком или автомобиль.
  bool _byCar = true;

  /// Оптимальный маршрут от Google Directions API.
  GoogleDirectionsResult? _route;

  List<PlacePrediction> _fromSuggestions = [];
  List<PlacePrediction> _toSuggestions = [];
  Timer? _debounce;

  /// Умная рекомендация (AI-совет)
  String? _recommendation;
  bool _loadingRec = false;

  /// Транспорт с сервера
  List<MapVehicle> _vehicles = [];
  Timer? _vehiclePollTimer;

  gmaps.BitmapDescriptor? _carIcon;
  gmaps.BitmapDescriptor? _busIcon;
  TrafficMetrics? _trafficMetrics;

  @override
  void initState() {
    super.initState();
    _startVehiclePolling();
    _initIcons();
    ThemeNotifier().addListener(_updateMapStyle);
  }

  @override
  void dispose() {
    ThemeNotifier().removeListener(_updateMapStyle);
    _vehiclePollTimer?.cancel();
    _debounce?.cancel();
    _fromController.dispose();
    _toController.dispose();
    _fromFocus.dispose();
    _toFocus.dispose();
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

  Future<void> _initIcons() async {
    _carIcon = await _buildMarkerIcon(Icons.directions_car, const Color(0xFFF59E0B)); // Желтая/Оранжевая для машин
    _busIcon = await _buildMarkerIcon(Icons.directions_bus, const Color(0xFF10B981)); // Зеленая для автобуса
    if (mounted) setState(() {});
  }

  Future<gmaps.BitmapDescriptor> _buildMarkerIcon(IconData iconData, Color color) async {
    final dart_ui.PictureRecorder pictureRecorder = dart_ui.PictureRecorder();
    final Canvas canvas = Canvas(pictureRecorder);
    const double size = 90;

    // Draw background circle
    final Paint paint = Paint()..color = color;
    canvas.drawCircle(const Offset(size / 2, size / 2), size / 2, paint);

    // Draw outline
    final Paint outline = Paint()
      ..color = Colors.white
      ..strokeWidth = 6
      ..style = PaintingStyle.stroke;
    canvas.drawCircle(const Offset(size / 2, size / 2), size / 2 - 3, outline);

    // Draw icon
    TextPainter textPainter = TextPainter(textDirection: TextDirection.ltr);
    textPainter.text = TextSpan(
      text: String.fromCharCode(iconData.codePoint),
      style: TextStyle(
        fontSize: size * 0.6,
        fontFamily: iconData.fontFamily,
        package: iconData.fontPackage,
        color: Colors.white,
      ),
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(size / 2 - textPainter.width / 2, size / 2 - textPainter.height / 2),
    );

    final img = await pictureRecorder.endRecording().toImage(size.toInt(), size.toInt());
    final data = await img.toByteData(format: dart_ui.ImageByteFormat.png);
    return gmaps.BitmapDescriptor.fromBytes(data!.buffer.asUint8List());
  }

  void _startVehiclePolling() {
    _fetchVehicles();
    _vehiclePollTimer = Timer.periodic(const Duration(seconds: 3), (_) {
      _fetchVehicles();
    });
  }

  Future<void> _fetchVehicles() async {
    try {
      final v = await ApiClient().getVehicles();
      // Fetch metrics less frequently
      TrafficMetrics? m;
      if (_vehicles.isEmpty || (DateTime.now().second % 15 == 0)) {
        try {
          m = await ApiClient().getTrafficMetrics();
        } catch (_) {}
      }

      if (mounted) {
        setState(() {
          _vehicles = v;
          if (m != null) _trafficMetrics = m;
        });
      }
    } catch (_) {}
  }


  void _onFromChanged(String value) {
    _clearRoute();
    _debounce?.cancel();
    if (value.trim().length < 2) {
      setState(() => _fromSuggestions = []);
      return;
    }
    _debounce = Timer(const Duration(milliseconds: 350), () async {
      final list = await getPlaceAutocomplete(value);
      if (mounted) setState(() => _fromSuggestions = list);
    });
  }

  void _onToChanged(String value) {
    _clearRoute();
    _debounce?.cancel();
    if (value.trim().length < 2) {
      setState(() => _toSuggestions = []);
      return;
    }
    _debounce = Timer(const Duration(milliseconds: 350), () async {
      final list = await getPlaceAutocomplete(value);
      if (mounted) setState(() => _toSuggestions = list);
    });
  }

  Future<void> _onFromSuggestionTap(PlacePrediction p) async {
    _fromFocus.unfocus();
    setState(() => _fromSuggestions = []);
    try {
      final detail = await getPlaceDetails(p.placeId);
      if (!mounted) return;
      _fromController.text = detail.formattedAddress;
      setState(() => a = LatLng(detail.lat, detail.lon));
      if (a != null && b != null) _buildRouteFromGoogle();
    } catch (_) {
      if (mounted) setState(() => error = 'Не удалось загрузить адрес');
    }
  }

  Future<void> _onToSuggestionTap(PlacePrediction p) async {
    _toFocus.unfocus();
    setState(() => _toSuggestions = []);
    try {
      final detail = await getPlaceDetails(p.placeId);
      if (!mounted) return;
      _toController.text = detail.formattedAddress;
      setState(() => b = LatLng(detail.lat, detail.lon));
      if (a != null && b != null) _buildRouteFromGoogle();
    } catch (_) {
      if (mounted) setState(() => error = 'Не удалось загрузить адрес');
    }
  }

  void _clearRoute() {
    setState(() {
      _route = null;
      error = null;
      _recommendation = null;
    });
  }

  Future<void> _buildRouteFromAddresses() async {
    final fromText = _fromController.text.trim();
    final toText = _toController.text.trim();
    if (fromText.isEmpty || toText.isEmpty) {
      setState(() => error = 'Введите адрес «Откуда» и «Куда»');
      return;
    }

    setState(() {
      loading = true;
      error = null;
      _route = null;
    });

    try {
      final origin = await getPlaceFromQuery(fromText);
      final destination = await getPlaceFromQuery(toText);
      if (!mounted) return;

      setState(() {
        a = LatLng(origin.lat, origin.lon);
        b = LatLng(destination.lat, destination.lon);
      });

      final result = await getGoogleDirections(
        originLat: a!.latitude,
        originLng: a!.longitude,
        destLat: b!.latitude,
        destLng: b!.longitude,
        mode: _byCar ? RouteMode.driving : RouteMode.walking,
      );
      if (!mounted) return;
      setState(() {
        _route = result;
        loading = false;
      });
      _fitBoundsToRoute();
      _fetchRecommendation();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  Future<void> _buildRouteFromGoogle() async {
    if (a == null || b == null) return;

    setState(() {
      loading = true;
      error = null;
      _route = null;
    });

    try {
      final result = await getGoogleDirections(
        originLat: a!.latitude,
        originLng: a!.longitude,
        destLat: b!.latitude,
        destLng: b!.longitude,
        mode: _byCar ? RouteMode.driving : RouteMode.walking,
      );
      if (!mounted) return;
      setState(() {
        _route = result;
        loading = false;
      });
      _fitBoundsToRoute();
      _fetchRecommendation();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  Future<void> _fetchRecommendation() async {
    if (!_byCar) return;
    setState(() => _loadingRec = true);
    try {
      final rec = await ApiClient().getTrafficRecommendation();
      if (mounted) {
        setState(() {
          _recommendation = rec['message'];
          _loadingRec = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loadingRec = false);
    }
  }

  void _fitBoundsToRoute() {
    if (_mapController == null || _route == null || _route!.points.length < 2)
      return;
    final pts = _route!.points;
    double minLat = pts.first.latitude, maxLat = pts.first.latitude;
    double minLng = pts.first.longitude, maxLng = pts.first.longitude;
    for (final p in pts) {
      if (p.latitude < minLat) minLat = p.latitude;
      if (p.latitude > maxLat) maxLat = p.latitude;
      if (p.longitude < minLng) minLng = p.longitude;
      if (p.longitude > maxLng) maxLng = p.longitude;
    }
    if (a != null) {
      if (a!.latitude < minLat) minLat = a!.latitude;
      if (a!.latitude > maxLat) maxLat = a!.latitude;
      if (a!.longitude < minLng) minLng = a!.longitude;
      if (a!.longitude > maxLng) maxLng = a!.longitude;
    }
    if (b != null) {
      if (b!.latitude < minLat) minLat = b!.latitude;
      if (b!.latitude > maxLat) maxLat = b!.latitude;
      if (b!.longitude < minLng) minLng = b!.longitude;
      if (b!.longitude > maxLng) maxLng = b!.longitude;
    }
    _mapController!.animateCamera(
      gmaps.CameraUpdate.newLatLngBounds(
        gmaps.LatLngBounds(
          southwest: gmaps.LatLng(minLat, minLng),
          northeast: gmaps.LatLng(maxLat, maxLng),
        ),
        80,
      ),
    );
  }

  gmaps.CameraPosition _initialCamera() {
    if (a != null) {
      return gmaps.CameraPosition(
        target: gmaps.LatLng(a!.latitude, a!.longitude),
        zoom: 12,
      );
    }
    return gmaps.CameraPosition(target: _kAstanaCenter, zoom: 12);
  }

  Set<gmaps.Polyline> _buildPolylines() {
    final Set<gmaps.Polyline> out = {};
    if (_route == null || _route!.points.length < 2) return out;
    final pts = _route!.points
        .whereType<LatLng>()
        .map((p) => gmaps.LatLng(p.latitude, p.longitude))
        .toList();
    out.add(gmaps.Polyline(
      polylineId: const gmaps.PolylineId('route'),
      points: pts,
      color: AppColors.primary,
      width: 6,
    ));
    return out;
  }

  Set<gmaps.Marker> _buildMarkers() {
    final Set<gmaps.Marker> out = {};
    if (a != null) {
      out.add(gmaps.Marker(
        markerId: const gmaps.MarkerId('from'),
        position: gmaps.LatLng(a!.latitude, a!.longitude),
        infoWindow: const gmaps.InfoWindow(title: 'Откуда'),
        icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(
            gmaps.BitmapDescriptor.hueGreen),
      ));
    }
    if (b != null) {
      out.add(gmaps.Marker(
        markerId: const gmaps.MarkerId('to'),
        position: gmaps.LatLng(b!.latitude, b!.longitude),
        infoWindow: const gmaps.InfoWindow(title: 'Куда'),
        icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(
            gmaps.BitmapDescriptor.hueRed),
      ));
    }
    for (final v in _vehicles) {
      out.add(gmaps.Marker(
        markerId: gmaps.MarkerId('veh_${v.id}'),
        position: gmaps.LatLng(v.lat, v.lon),
        infoWindow:
            gmaps.InfoWindow(title: v.type == 'bus' ? 'Автобус' : 'Такси/Авто'),
        icon: (v.type == 'bus' ? _busIcon : _carIcon) ??
            gmaps.BitmapDescriptor.defaultMarkerWithHue(v.type == 'bus'
                ? gmaps.BitmapDescriptor.hueAzure
                : gmaps.BitmapDescriptor.hueYellow),
        anchor: const Offset(0.5, 0.5),
      ));
    }
    return out;
  }

  Color _getTrafficColor(int score) {
    if (score <= 3) return const Color(0xFF10B981); // Green
    if (score <= 6) return const Color(0xFFF59E0B); // Orange
    return const Color(0xFFEF4444); // Red
  }

  Widget _buildTrafficScore() {
    final score = _trafficMetrics?.globalScore ?? 0;
    final color = _getTrafficColor(score);

    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: dart_ui.ImageFilter.blur(sigmaX: 8, sigmaY: 8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.8),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withOpacity(0.5), width: 2),
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(0.1),
                blurRadius: 10,
                spreadRadius: 2,
              )
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: Text(
                  '$score',
                  style: TextStyle(
                    color: color,
                    fontWeight: FontWeight.w900,
                    fontSize: 18,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'ПРОБКИ',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 0.5,
                      color: Colors.black54,
                    ),
                  ),
                  Text(
                    _trafficMetrics?.level ?? '',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final hasRoute = _route != null && _route!.points.length >= 2;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        title: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor.withOpacity(0.85),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4)),
            ],
          ),
          child: Text('Навигатор',
              style: TextStyle(
                fontWeight: FontWeight.w800,
                fontSize: 18,
                color: Theme.of(context).textTheme.titleLarge?.color ?? AppColors.primaryDark,
              )),
        ),
        actions: [
          if (loading)
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  shape: BoxShape.circle,
                  boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 8)],
                ),
                child: const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
        ],
      ),
      body: Stack(
        children: [
          // 1. Full-screen map
          gmaps.GoogleMap(
            initialCameraPosition: _initialCamera(),
            onMapCreated: (c) {
              _mapController = c;
              _updateMapStyle();
            },
            polylines: _buildPolylines(),
            markers: _buildMarkers(),
            mapToolbarEnabled: false,
            myLocationButtonEnabled: false,
            zoomControlsEnabled: false,
            trafficEnabled: _byCar,
            padding: const EdgeInsets.only(top: 360, bottom: 40),
          ),
          // 1.1 Traffic Score Indicator
          if (_trafficMetrics != null)
            Positioned(
              top: MediaQuery.of(context).padding.top + 80,
              right: 16,
              child: _buildTrafficScore(),
            ),
          // 2. Glassmorphism overlay on top
          SafeArea(
            child: Align(
              alignment: Alignment.topCenter,
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 20, 16, 12),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(24),
                        child: BackdropFilter(
                          filter: dart_ui.ImageFilter.blur(sigmaX: 16, sigmaY: 16),
                          child: Container(
                            padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
                            decoration: BoxDecoration(
                              color: Theme.of(context).cardColor.withOpacity(0.85),
                              borderRadius: BorderRadius.circular(24),
                              border: Border.all(
                                color: Theme.of(context).brightness == Brightness.dark 
                                  ? Colors.white.withOpacity(0.12)
                                  : Colors.white.withOpacity(0.5),
                                width: 1.5,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.08),
                                  blurRadius: 24,
                                  offset: const Offset(0, 8),
                                ),
                              ],
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                // Откуда
                                TextField(
                                  controller: _fromController,
                                  focusNode: _fromFocus,
                                  decoration: InputDecoration(
                                    labelText: 'Откуда',
                                    hintText: 'Адрес или место',
                                    prefixIcon: Container(
                                      margin: const EdgeInsets.only(right: 12),
                                      padding: const EdgeInsets.all(10),
                                      decoration: BoxDecoration(
                                        color:
                                            AppColors.primary.withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: const Icon(
                                          Icons.trip_origin_rounded,
                                          size: 20,
                                          color: AppColors.primary),
                                    ),
                                    prefixIconConstraints: const BoxConstraints(
                                        minWidth: 48, minHeight: 48),
                                    filled: true,
                                    fillColor: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.6),
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(14),
                                      borderSide: BorderSide.none,
                                    ),
                                    enabledBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(14),
                                      borderSide: BorderSide(
                                          color: AppColors.divider
                                              .withOpacity(0.6)),
                                    ),
                                    focusedBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(14),
                                      borderSide: const BorderSide(
                                          color: AppColors.primary, width: 2),
                                    ),
                                    contentPadding: const EdgeInsets.symmetric(
                                        horizontal: 16, vertical: 14),
                                  ),
                                  textInputAction: TextInputAction.next,
                                  onChanged: _onFromChanged,
                                  onTap: () =>
                                      setState(() => _toSuggestions = []),
                                ),
                                if (_fromSuggestions.isNotEmpty &&
                                    _fromFocus.hasFocus) ...[
                                  const SizedBox(height: 10),
                                  Container(
                                    constraints:
                                        const BoxConstraints(maxHeight: 220),
                                    decoration: BoxDecoration(
                                      color: Theme.of(context).cardColor,
                                      borderRadius: BorderRadius.circular(14),
                                      border: Border.all(
                                          color: AppColors.divider
                                              .withOpacity(0.6)),
                                      boxShadow: [
                                        BoxShadow(
                                          color: Colors.black.withOpacity(0.08),
                                          blurRadius: 16,
                                          offset: const Offset(0, 4),
                                        ),
                                      ],
                                    ),
                                    clipBehavior: Clip.antiAlias,
                                    child: ListView.separated(
                                      padding: const EdgeInsets.symmetric(
                                          vertical: 6),
                                      shrinkWrap: true,
                                      itemCount: _fromSuggestions.length,
                                      separatorBuilder: (_, __) => Divider(
                                          height: 1,
                                          color: AppColors.divider
                                              .withOpacity(0.5)),
                                      itemBuilder: (context, i) {
                                        final p = _fromSuggestions[i];
                                        return Material(
                                          color: Colors.transparent,
                                          child: InkWell(
                                            onTap: () =>
                                                _onFromSuggestionTap(p),
                                            child: Padding(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                      horizontal: 16,
                                                      vertical: 12),
                                              child: Row(
                                                children: [
                                                  Icon(Icons.place_rounded,
                                                      size: 22,
                                                      color: AppColors.primary
                                                          .withOpacity(0.9)),
                                                  const SizedBox(width: 14),
                                                  Expanded(
                                                    child: Text(
                                                      p.description,
                                                      style: const TextStyle(
                                                          fontSize: 14,
                                                          color: AppColors
                                                              .textPrimary,
                                                          height: 1.3),
                                                      maxLines: 2,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                        );
                                      },
                                    ),
                                  ),
                                ],
                                const SizedBox(height: 14),
                                // Куда
                                // Куда
                                TextField(
                                  controller: _toController,
                                  focusNode: _toFocus,
                                  decoration: InputDecoration(
                                    labelText: 'Куда',
                                    hintText: 'Адрес или место',
                                    prefixIcon: Container(
                                      margin: const EdgeInsets.only(right: 12),
                                      padding: const EdgeInsets.all(10),
                                      decoration: BoxDecoration(
                                        color:
                                            AppColors.primary.withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: const Icon(
                                          Icons.location_on_rounded,
                                          size: 20,
                                          color: AppColors.primary),
                                    ),
                                    prefixIconConstraints: const BoxConstraints(
                                        minWidth: 48, minHeight: 48),
                                    filled: true,
                                    fillColor: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.6),
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(14),
                                      borderSide: BorderSide.none,
                                    ),
                                    enabledBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(14),
                                      borderSide: BorderSide(
                                          color: AppColors.divider
                                              .withOpacity(0.6)),
                                    ),
                                    focusedBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(14),
                                      borderSide: const BorderSide(
                                          color: AppColors.primary, width: 2),
                                    ),
                                    contentPadding: const EdgeInsets.symmetric(
                                        horizontal: 16, vertical: 14),
                                  ),
                                  textInputAction: TextInputAction.done,
                                  onChanged: _onToChanged,
                                  onSubmitted: (_) =>
                                      _buildRouteFromAddresses(),
                                  onTap: () =>
                                      setState(() => _fromSuggestions = []),
                                ),
                                if (_toSuggestions.isNotEmpty &&
                                    _toFocus.hasFocus) ...[
                                  const SizedBox(height: 10),
                                  Container(
                                    constraints:
                                        const BoxConstraints(maxHeight: 220),
                                    decoration: BoxDecoration(
                                      color: Theme.of(context).cardColor,
                                      borderRadius: BorderRadius.circular(14),
                                      border: Border.all(
                                          color: AppColors.divider
                                              .withOpacity(0.6)),
                                      boxShadow: [
                                        BoxShadow(
                                          color: Colors.black.withOpacity(0.08),
                                          blurRadius: 16,
                                          offset: const Offset(0, 4),
                                        ),
                                      ],
                                    ),
                                    clipBehavior: Clip.antiAlias,
                                    child: ListView.separated(
                                      padding: const EdgeInsets.symmetric(
                                          vertical: 6),
                                      shrinkWrap: true,
                                      itemCount: _toSuggestions.length,
                                      separatorBuilder: (_, __) => Divider(
                                          height: 1,
                                          color: AppColors.divider
                                              .withOpacity(0.5)),
                                      itemBuilder: (context, i) {
                                        final p = _toSuggestions[i];
                                        return Material(
                                          color: Colors.transparent,
                                          child: InkWell(
                                            onTap: () => _onToSuggestionTap(p),
                                            child: Padding(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                      horizontal: 16,
                                                      vertical: 12),
                                              child: Row(
                                                children: [
                                                  Icon(Icons.place_rounded,
                                                      size: 22,
                                                      color: AppColors.primary
                                                          .withOpacity(0.9)),
                                                  const SizedBox(width: 14),
                                                  Expanded(
                                                    child: Text(
                                                      p.description,
                                                      style: TextStyle(
                                                          fontSize: 14,
                                                          color: Theme.of(context).textTheme.bodyLarge?.color,
                                                          height: 1.3),
                                                      maxLines: 2,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                        );
                                      },
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 18),
                                // Пешком / Автомобиль
                                Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: BoxDecoration(
                                    color:
                                        AppColors.background.withOpacity(0.8),
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(
                                        color:
                                            AppColors.divider.withOpacity(0.5)),
                                  ),
                                  child: Row(
                                    children: [
                                      Expanded(
                                        child: Material(
                                          color: _byCar
                                              ? Colors.transparent
                                              : AppColors.primary,
                                          borderRadius:
                                              BorderRadius.circular(12),
                                          child: InkWell(
                                            borderRadius:
                                                BorderRadius.circular(12),
                                            onTap: () {
                                              setState(() {
                                                _byCar = false;
                                                if (a == null || b == null)
                                                  _clearRoute();
                                              });
                                              if (a != null && b != null)
                                                _buildRouteFromGoogle();
                                            },
                                            child: Padding(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                      vertical: 12),
                                              child: Row(
                                                mainAxisAlignment:
                                                    MainAxisAlignment.center,
                                                children: [
                                                  Icon(
                                                    Icons
                                                        .directions_walk_rounded,
                                                    size: 20,
                                                    color: _byCar
                                                        ? AppColors
                                                            .textSecondary
                                                        : Colors.white,
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Text(
                                                    'Пешком',
                                                    style: TextStyle(
                                                      fontWeight:
                                                          FontWeight.w600,
                                                      fontSize: 14,
                                                      color: _byCar
                                                          ? AppColors
                                                              .textSecondary
                                                          : Colors.white,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 4),
                                      Expanded(
                                        child: Material(
                                          color: _byCar
                                              ? AppColors.primary
                                              : Colors.transparent,
                                          borderRadius:
                                              BorderRadius.circular(12),
                                          child: InkWell(
                                            borderRadius:
                                                BorderRadius.circular(12),
                                            onTap: () {
                                              setState(() {
                                                _byCar = true;
                                                if (a == null || b == null)
                                                  _clearRoute();
                                              });
                                              if (a != null && b != null)
                                                _buildRouteFromGoogle();
                                            },
                                            child: Padding(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                      vertical: 12),
                                              child: Row(
                                                mainAxisAlignment:
                                                    MainAxisAlignment.center,
                                                children: [
                                                  Icon(
                                                    Icons
                                                        .directions_car_rounded,
                                                    size: 20,
                                                    color: _byCar
                                                        ? Colors.white
                                                        : AppColors
                                                            .textSecondary,
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Text(
                                                    'Автомобиль',
                                                    style: TextStyle(
                                                      fontWeight:
                                                          FontWeight.w600,
                                                      fontSize: 14,
                                                      color: _byCar
                                                          ? Colors.white
                                                          : AppColors
                                                              .textSecondary,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                if (hasRoute) ...[
                                  const SizedBox(height: 16),
                                  Container(
                                    padding: const EdgeInsets.all(16),
                                    decoration: BoxDecoration(
                                      gradient: LinearGradient(
                                        colors: [
                                          AppColors.primary.withOpacity(0.12),
                                          AppColors.primary.withOpacity(0.06),
                                        ],
                                        begin: Alignment.topLeft,
                                        end: Alignment.bottomRight,
                                      ),
                                      borderRadius: BorderRadius.circular(14),
                                      border: Border.all(
                                          color: AppColors.primary
                                              .withOpacity(0.2)),
                                    ),
                                    child: Row(
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.all(10),
                                          decoration: BoxDecoration(
                                            color: AppColors.primary
                                                .withOpacity(0.15),
                                            borderRadius:
                                                BorderRadius.circular(12),
                                          ),
                                          child: const Icon(Icons.route_rounded,
                                              color: AppColors.primary,
                                              size: 24),
                                        ),
                                        const SizedBox(width: 14),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              if (_route!.durationInTrafficText !=
                                                      null &&
                                                  _byCar) ...[
                                                Text(
                                                  _route!
                                                      .durationInTrafficText!,
                                                  style: const TextStyle(
                                                    fontWeight: FontWeight.w700,
                                                    fontSize: 18,
                                                    color: AppColors.primary,
                                                    letterSpacing: -0.3,
                                                  ),
                                                ),
                                                const SizedBox(height: 2),
                                                Text(
                                                  'С учётом пробок • ${_route!.durationText} без трафика${_route!.distanceText != null ? ' • ${_route!.distanceText}' : ''}',
                                                  style: TextStyle(
                                                    fontSize: 12,
                                                    color:
                                                        AppColors.textSecondary,
                                                    height: 1.3,
                                                  ),
                                                ),
                                              ] else
                                                Text(
                                                  _route!.durationText,
                                                  style: const TextStyle(
                                                    fontWeight: FontWeight.w700,
                                                    fontSize: 18,
                                                    color: AppColors.primary,
                                                    letterSpacing: -0.3,
                                                  ),
                                                ),
                                              if (_route!.distanceText !=
                                                      null &&
                                                  (_route!.durationInTrafficText ==
                                                          null ||
                                                      !_byCar))
                                                Padding(
                                                  padding:
                                                      const EdgeInsets.only(
                                                          top: 2),
                                                  child: Text(
                                                    _route!.distanceText!,
                                                    style: TextStyle(
                                                        fontSize: 12,
                                                        color: AppColors
                                                            .textSecondary),
                                                  ),
                                                ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                    if (_recommendation != null && _byCar)
                      Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 4),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(20),
                          child: BackdropFilter(
                            filter: dart_ui.ImageFilter.blur(sigmaX: 16, sigmaY: 16),
                            child: Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AppColors.primary.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(
                                    color: Colors.white.withOpacity(0.5)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.psychology_outlined,
                                      color: AppColors.primary, size: 28),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          'AI СОВЕТ',
                                          style: TextStyle(
                                            fontSize: 11,
                                            fontWeight: FontWeight.w800,
                                            color: AppColors.primary,
                                            letterSpacing: 0.5,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          _recommendation!,
                                          style: const TextStyle(
                                            fontSize: 13,
                                            color: AppColors.textPrimary,
                                            height: 1.4,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    if (error != null)
                      Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 6),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(20),
                          child: BackdropFilter(
                            filter: dart_ui.ImageFilter.blur(sigmaX: 16, sigmaY: 16),
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 16, vertical: 12),
                              decoration: BoxDecoration(
                                color: Colors.red.withOpacity(Theme.of(context).brightness == Brightness.dark ? 0.15 : 0.08),
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(color: Colors.red.withOpacity(0.3)),
                              ),
                              child: Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(6),
                                    decoration: BoxDecoration(
                                      color: Colors.red.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: const Icon(
                                        Icons.error_outline_rounded,
                                        color: Color(0xFFDC2626),
                                        size: 20),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                      child: Text(
                                        error!,
                                        style: TextStyle(
                                            color: Theme.of(context).brightness == Brightness.dark ? Colors.red.shade200 : const Color(0xFFB91C1C),
                                            fontSize: 13,
                                            height: 1.3),
                                      ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
