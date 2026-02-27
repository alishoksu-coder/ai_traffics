import 'dart:async';

import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;
import 'package:latlong2/latlong.dart';

import 'api.dart';
import 'package:traffic_app/common.dart';

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

  @override
  void dispose() {
    _debounce?.cancel();
    _fromController.dispose();
    _toController.dispose();
    _fromFocus.dispose();
    _toFocus.dispose();
    super.dispose();
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
    } catch (_) {
      if (mounted) setState(() => error = 'Не удалось загрузить адрес');
    }
  }

  void _clearRoute() {
    setState(() {
      _route = null;
      error = null;
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
    } catch (e) {
      if (!mounted) return;
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  void _fitBoundsToRoute() {
    if (_mapController == null || _route == null || _route!.points.length < 2) return;
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
    final pts = _route!
        .points
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

  @override
  Widget build(BuildContext context) {
    final hasRoute = _route != null && _route!.points.length >= 2;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: whiteAppBar(
        'Навигатор',
        actions: [
          if (loading)
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: Center(
                child: SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 10),
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.06),
                    blurRadius: 20,
                    offset: const Offset(0, 6),
                  ),
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.04),
                    blurRadius: 30,
                    offset: const Offset(0, 2),
                  ),
                ],
                border: Border.all(
                  color: AppColors.divider.withOpacity(0.5),
                  width: 1,
                ),
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
                          color: AppColors.primary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.trip_origin_rounded, size: 20, color: AppColors.primary),
                      ),
                      prefixIconConstraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                      filled: true,
                      fillColor: AppColors.background.withOpacity(0.6),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide.none,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide(color: AppColors.divider.withOpacity(0.6)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: const BorderSide(color: AppColors.primary, width: 2),
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    ),
                    textInputAction: TextInputAction.next,
                    onChanged: _onFromChanged,
                    onTap: () => setState(() => _toSuggestions = []),
                  ),
                  if (_fromSuggestions.isNotEmpty && _fromFocus.hasFocus) ...[
                    const SizedBox(height: 10),
                    Container(
                      constraints: const BoxConstraints(maxHeight: 220),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppColors.divider.withOpacity(0.6)),
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
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        shrinkWrap: true,
                        itemCount: _fromSuggestions.length,
                        separatorBuilder: (_, __) => Divider(height: 1, color: AppColors.divider.withOpacity(0.5)),
                        itemBuilder: (context, i) {
                          final p = _fromSuggestions[i];
                          return Material(
                            color: Colors.transparent,
                            child: InkWell(
                              onTap: () => _onFromSuggestionTap(p),
                              child: Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                                child: Row(
                                  children: [
                                    Icon(Icons.place_rounded, size: 22, color: AppColors.primary.withOpacity(0.9)),
                                    const SizedBox(width: 14),
                                    Expanded(
                                      child: Text(
                                        p.description,
                                        style: const TextStyle(fontSize: 14, color: AppColors.textPrimary, height: 1.3),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
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
                          color: AppColors.primary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.location_on_rounded, size: 20, color: AppColors.primary),
                      ),
                      prefixIconConstraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                      filled: true,
                      fillColor: AppColors.background.withOpacity(0.6),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide.none,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide(color: AppColors.divider.withOpacity(0.6)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: const BorderSide(color: AppColors.primary, width: 2),
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    ),
                    textInputAction: TextInputAction.done,
                    onChanged: _onToChanged,
                    onSubmitted: (_) => _buildRouteFromAddresses(),
                    onTap: () => setState(() => _fromSuggestions = []),
                  ),
                  if (_toSuggestions.isNotEmpty && _toFocus.hasFocus) ...[
                    const SizedBox(height: 10),
                    Container(
                      constraints: const BoxConstraints(maxHeight: 220),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppColors.divider.withOpacity(0.6)),
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
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        shrinkWrap: true,
                        itemCount: _toSuggestions.length,
                        separatorBuilder: (_, __) => Divider(height: 1, color: AppColors.divider.withOpacity(0.5)),
                        itemBuilder: (context, i) {
                          final p = _toSuggestions[i];
                          return Material(
                            color: Colors.transparent,
                            child: InkWell(
                              onTap: () => _onToSuggestionTap(p),
                              child: Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                                child: Row(
                                  children: [
                                    Icon(Icons.place_rounded, size: 22, color: AppColors.primary.withOpacity(0.9)),
                                    const SizedBox(width: 14),
                                    Expanded(
                                      child: Text(
                                        p.description,
                                        style: const TextStyle(fontSize: 14, color: AppColors.textPrimary, height: 1.3),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
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
                  const SizedBox(height: 18),
                  // Пешком / Автомобиль
                  Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: AppColors.background.withOpacity(0.8),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppColors.divider.withOpacity(0.5)),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Material(
                            color: _byCar ? Colors.transparent : AppColors.primary,
                            borderRadius: BorderRadius.circular(12),
                            child: InkWell(
                              borderRadius: BorderRadius.circular(12),
                              onTap: () {
                                setState(() {
                                  _byCar = false;
                                  if (a == null || b == null) _clearRoute();
                                });
                                if (a != null && b != null) _buildRouteFromGoogle();
                              },
                              child: Padding(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      Icons.directions_walk_rounded,
                                      size: 20,
                                      color: _byCar ? AppColors.textSecondary : Colors.white,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      'Пешком',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w600,
                                        fontSize: 14,
                                        color: _byCar ? AppColors.textSecondary : Colors.white,
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
                            color: _byCar ? AppColors.primary : Colors.transparent,
                            borderRadius: BorderRadius.circular(12),
                            child: InkWell(
                              borderRadius: BorderRadius.circular(12),
                              onTap: () {
                                setState(() {
                                  _byCar = true;
                                  if (a == null || b == null) _clearRoute();
                                });
                                if (a != null && b != null) _buildRouteFromGoogle();
                              },
                              child: Padding(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      Icons.directions_car_rounded,
                                      size: 20,
                                      color: _byCar ? Colors.white : AppColors.textSecondary,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      'Автомобиль',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w600,
                                        fontSize: 14,
                                        color: _byCar ? Colors.white : AppColors.textSecondary,
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
                        border: Border.all(color: AppColors.primary.withOpacity(0.2)),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: AppColors.primary.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(Icons.route_rounded, color: AppColors.primary, size: 24),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                if (_route!.durationInTrafficText != null && _byCar) ...[
                                  Text(
                                    _route!.durationInTrafficText!,
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
                                      color: AppColors.textSecondary,
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
                                if (_route!.distanceText != null && (_route!.durationInTrafficText == null || !_byCar))
                                  Padding(
                                    padding: const EdgeInsets.only(top: 2),
                                    child: Text(
                                      _route!.distanceText!,
                                      style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
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
          if (error != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFFECACA)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.red.withOpacity(0.06),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.error_outline_rounded, color: Color(0xFFDC2626), size: 20),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        error!,
                        style: const TextStyle(color: Color(0xFFB91C1C), fontSize: 13, height: 1.3),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          Expanded(
            child: gmaps.GoogleMap(
              initialCameraPosition: _initialCamera(),
              onMapCreated: (c) => _mapController = c,
              polylines: _buildPolylines(),
              markers: const {},
              mapToolbarEnabled: true,
              trafficEnabled: _byCar,
            ),
          ),
        ],
      ),
    );
  }
}
