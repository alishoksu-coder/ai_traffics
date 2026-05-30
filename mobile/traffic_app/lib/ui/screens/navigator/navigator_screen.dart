import 'dart:async';
import 'dart:ui' as dart_ui;

import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;
import 'package:latlong2/latlong.dart';

import '../../../services/api_client.dart';
import '../../../services/google_maps_service.dart';
import '../../../models/models.dart';
import 'package:traffic_app/core/common.dart';
import '../../../core/theme_notifier.dart';
import '../../../core/map_styles.dart';
import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';

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


  bool _antiStressMode = false;
  bool _barrierFreeMode = false;
  Map<String, dynamic>? _parkingData;

  UserProfile? _userProfile;

  bool _isForecastMode = false;
  List<RoadSegment> _futureSegments = [];
  Map<String, dynamic>? _multimodalRec;
  bool _loadingMultimodal = false;
  List<Map<String, dynamic>> _arPoints = [];

  @override
  void initState() {
    super.initState();
    _loadProfile();
    ThemeNotifier().addListener(_updateMapStyle);
    globalRouteRequest.addListener(_onGlobalRouteRequest);
    
    if (globalRouteRequest.value != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _onGlobalRouteRequest();
      });
    }
  }

  @override
  void dispose() {
    globalRouteRequest.removeListener(_onGlobalRouteRequest);
    ThemeNotifier().removeListener(_updateMapStyle);
    _debounce?.cancel();
    _fromController.dispose();
    _toController.dispose();
    _fromFocus.dispose();
    _toFocus.dispose();
    super.dispose();
  }

  void _onGlobalRouteRequest() {
    final req = globalRouteRequest.value;
    if (req != null && mounted) {
      _toController.text = req.destinationName;
      setState(() {
        b = LatLng(req.destinationLat, req.destinationLng);
      });
      _useMyLocation();
      globalRouteRequest.value = null; // очищаем после обработки
    }
  }

  Future<void> _loadProfile() async {
    final profile = await ApiClient().getUserProfile();
    if (mounted) {
      setState(() {
        _userProfile = profile;
      });
    }
  }

  void _handleShortcutTap(String type) async {
    final isHome = type == 'home';
    final savedLat = isHome ? _userProfile?.homeLat : _userProfile?.workLat;
    final savedLng = isHome ? _userProfile?.homeLng : _userProfile?.workLng;
    final savedTitle = isHome ? _userProfile?.homeTitle : _userProfile?.workTitle;
    final label = isHome ? 'Үйде' : 'Жұмыс';

    if (savedLat != null && savedLng != null) {
      _toController.text = savedTitle ?? (isHome ? "Үй" : "Жұмыс");
      setState(() => b = LatLng(savedLat, savedLng));
      _useMyLocation();
    } else {
      // Вызываем красивое окно как на дизайне
      final place = await _showAddShortcutBottomSheet(type, label);

      if (place != null) {
        try {
          setState(() => this.loading = true);
          await ApiClient().saveUserShortcut(type, place.formattedAddress, place.lat, place.lon);
          await _loadProfile(); // Обновить кэш профиля
          
          _toController.text = place.formattedAddress;
          setState(() => b = LatLng(place.lat, place.lon));
          _useMyLocation();
        } catch (e) {
          if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Ошибка сохранения: $e')));
        } finally {
          if (mounted) setState(() => this.loading = false);
        }
      }
    }
  }

  Future<PlaceResult?> _showAddShortcutBottomSheet(String type, String label) async {
    final titleControl = TextEditingController(text: type == 'home' ? 'Үй' : 'Жұмыс');
    final addressControl = TextEditingController();
    bool sheetLoading = false;

    return await showModalBottomSheet<PlaceResult>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setStateSheet) {
            final isDark = Theme.of(ctx).brightness == Brightness.dark;
            final purpleColor = const Color(0xFF4C45E5);
            
            return Padding(
              padding: EdgeInsets.only(bottom: MediaQuery.of(ctx).viewInsets.bottom),
              child: Container(
                decoration: BoxDecoration(
                  color: isDark ? const Color(0xFF0F172A) : Colors.white,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Фиолетовая шапка
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.only(top: 24, left: 20, right: 20, bottom: 40),
                      decoration: BoxDecoration(
                        color: purpleColor,
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              GestureDetector(
                                onTap: () => Navigator.pop(ctx),
                                child: const Icon(Icons.close_rounded, color: Colors.white, size: 28),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                          Row(
                            children: [
                              Container(
                                width: 64,
                                height: 64,
                                decoration: BoxDecoration(
                                  color: Colors.white.withValues(alpha: 0.15),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(color: Colors.white.withValues(alpha: 0.3)),
                                ),
                                child: Icon(
                                  type == 'home' ? Icons.home_rounded : Icons.business_center_rounded,
                                  color: Colors.white,
                                  size: 32,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Новый адрес: $label',
                                      style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w700),
                                    ),
                                    const SizedBox(height: 6),
                                    const Text(
                                      'Укажите локацию, чтобы быстро строить маршрут в один клик.',
                                      style: TextStyle(color: Colors.white70, fontSize: 13, height: 1.3),
                                    ),
                                  ],
                                ),
                              )
                            ],
                          ),
                        ],
                      ),
                    ),
                    
                    // Белая рабочая зона 
                    Container(
                      transform: Matrix4.translationValues(0, -20, 0),
                      padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
                      decoration: BoxDecoration(
                        color: isDark ? const Color(0xFF0F172A) : Colors.white,
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.edit_note_rounded, size: 20, color: isDark ? Colors.indigoAccent : Colors.indigo.shade800),
                              const SizedBox(width: 8),
                              Text('Негізгі', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: isDark ? Colors.white : Colors.black87)),
                            ],
                          ),
                          const SizedBox(height: 12),
                          _buildPremiumTextField(titleControl, 'Название', Icons.storefront_rounded),
                          
                          const SizedBox(height: 24),
                          Row(
                            children: [
                              Icon(Icons.location_on_rounded, size: 20, color: isDark ? Colors.indigoAccent : Colors.indigo.shade800),
                              const SizedBox(width: 8),
                              Text('Описание и адрес', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: isDark ? Colors.white : Colors.black87)),
                            ],
                          ),
                          const SizedBox(height: 12),
                          _buildPremiumTextField(addressControl, 'Мысалы: Сығанақ 17, Астана...', Icons.search_rounded),

                          const SizedBox(height: 24),
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: purpleColor.withValues(alpha: 0.06),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Icon(Icons.remove_red_eye_outlined, color: purpleColor, size: 20),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Text(
                                    type == 'home' 
                                      ? 'После сохранения, этот маршрут будет доступен всем вашим устройствам на главном экране.'
                                      : 'Позже вы сможете изменить этот адрес в настройках профиля приложения.',
                                    style: TextStyle(fontSize: 12, height: 1.4, color: isDark ? Colors.white70 : Colors.black87),
                                  ),
                                ),
                              ],
                            ),
                          ),

                          const SizedBox(height: 32),
                          SizedBox(
                            width: double.infinity,
                            height: 56,
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: purpleColor,
                                foregroundColor: Colors.white,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                                elevation: 0,
                              ),
                              onPressed: sheetLoading ? null : () async {
                                if (addressControl.text.trim().isEmpty) {
                                  ScaffoldMessenger.of(ctx).showSnackBar(const SnackBar(content: Text('Мекенжайды енгізіңіз')));
                                  return;
                                }
                                setStateSheet(() => sheetLoading = true);
                                try {
                                  final res = await getPlaceFromQuery(addressControl.text);
                                  Navigator.pop(ctx, res);
                                } catch (e) {
                                  setStateSheet(() => sheetLoading = false);
                                  ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text('Ештеңе табылмады, сұранысты нақтылаңыз')));
                                }
                              },
                              child: sheetLoading 
                                ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                                : const Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.check_circle_outline_rounded, size: 22),
                                      SizedBox(width: 8),
                                      Text('Мекенжайды сақтау', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                                    ],
                                  ),
                            ),
                          )
                        ],
                      ),
                    )
                  ],
                ),
              ),
            );
          }
        );
      }
    );
  }

  Widget _buildPremiumTextField(TextEditingController ctrl, String hint, IconData icon) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return TextField(
      controller: ctrl,
      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w400),
        prefixIcon: Icon(icon, color: isDark ? Colors.white54 : Colors.grey.shade600, size: 20),
        filled: true,
        fillColor: isDark ? const Color(0xFF1E293B) : const Color(0xFFF8FAFC),
        contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: isDark ? Colors.white12 : Colors.grey.shade200),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: isDark ? Colors.white12 : Colors.grey.shade200),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF4C45E5), width: 1.5),
        ),
      ),
    );
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
      if (mounted) setState(() => error = 'Мекенжайды жүктеу мүмкін болмады');
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
      if (mounted) setState(() => error = 'Мекенжайды жүктеу мүмкін болмады');
    }
  }

  void _swapAddresses() {
    final tempText = _fromController.text;
    _fromController.text = _toController.text;
    _toController.text = tempText;

    final tempA = a;
    a = b;
    b = tempA;

    if (a != null && b != null) {
      _buildRouteFromGoogle();
    } else {
      _clearRoute();
    }
  }

  Future<void> _useMyLocation() async {
    setState(() => loading = true);
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('Геолокация қызметтері өшірілген.');
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw Exception('Геолокацияға рұқсат берілмеді.');
        }
      }
      
      if (permission == LocationPermission.deniedForever) {
        throw Exception('Геолокацияға рұқсат біржола бұғатталған.');
      } 

      Position position = await Geolocator.getCurrentPosition();
      final lat = position.latitude;
      final lng = position.longitude;
      
      final address = await getAddressForLatLng(lat, lng);
      
      if (!mounted) return;
      setState(() {
        a = LatLng(lat, lng);
        _fromController.text = address;
        error = null;
      });
      
      if (b != null) {
        _buildRouteFromGoogle();
      } else {
        setState(() => loading = false);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  void _clearRoute() {
    setState(() {
      _route = null;
      error = null;
      _multimodalRec = null;
      _isForecastMode = false;
      _futureSegments.clear();
      _parkingData = null;
    });
  }

  Future<void> _buildRouteFromAddresses() async {
    final fromText = _fromController.text.trim();
    final toText = _toController.text.trim();
    if (fromText.isEmpty || toText.isEmpty) {
      setState(() => error = '«Қайдан» және «Қайда» мекенжайларын енгізіңіз');
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
        antiStress: _antiStressMode,
        barrierFree: _barrierFreeMode,
      );
      if (!mounted) return;
      setState(() {
        _route = result;
        loading = false;
        _isForecastMode = false;
        _futureSegments.clear();
        _multimodalRec = null;
      });
      _fitBoundsToRoute();
      if (_byCar) _fetchParking();
      if (!_byCar && _barrierFreeMode) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('✅ Инклюзивті маршрут құрылды (баспалдақтарсыз)'),
          backgroundColor: Colors.green,
        ));
      }
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
        antiStress: _antiStressMode,
        barrierFree: _barrierFreeMode,
      );
      if (!mounted) return;
      setState(() {
        _route = result;
        loading = false;
        _isForecastMode = false;
        _futureSegments.clear();
        _multimodalRec = null;
      });
      _fitBoundsToRoute();
      if (_byCar) _fetchParking();
      if (!_byCar && _barrierFreeMode) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('✅ Инклюзивті маршрут құрылды (баспалдақтарсыз)'),
          backgroundColor: Colors.green,
        ));
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  Future<void> _fetchParking() async {
    if (_route == null || !_byCar) return;
    int minutes = (_route!.durationSeconds / 60).round();
    try {
      final pData = await ApiClient().getParkings(minutes);
      if (mounted) setState(() => _parkingData = pData);
    } catch (_) {}
  }



  Future<void> _fetchForecastAndMultimodal() async {
    if (_route == null) return;
    setState(() {
      _isForecastMode = true;
      _loadingMultimodal = true;
    });
    
    try {
      final fut = await ApiClient().getRoadSegments(30);
      _futureSegments = fut;

      final dist = _route!.distanceValue;
      final dur = _route!.durationSeconds;
      
      final mm = await ApiClient().getMultimodalAnalysis(dur, dist);
      if (mounted) {
        setState(() {
          _multimodalRec = mm;
          _loadingMultimodal = false;
        });
        
        final rec = mm['recommend_transfer'] == true;
        if (rec) {
           ScaffoldMessenger.of(context).showSnackBar(SnackBar(
             content: Text(mm['message'] ?? 'Ұсыныс: мультимодальдық маршрут тиімді.'),
             backgroundColor: Colors.indigo,
           ));
        } else {
           ScaffoldMessenger.of(context).showSnackBar(SnackBar(
             content: Text(mm['message'] ?? 'Сіздің маршрутыңыз ең тиімді.'),
             backgroundColor: Colors.green,
           ));
        }
      }
      
      // AR нүктелерін де жүктеу
      final arPts = await ApiClient().getArPoints(horizon: 30);
      if (mounted) {
        setState(() => _arPoints = arPts);
      }
    } catch (e) {
      if (mounted) setState(() => _loadingMultimodal = false);
      print('Multimodal Error: $e');
    }
  }

  void _openStreetView(double lat, double lng) async {
    // Google Street View URL scheme
    final url = Uri.parse(
      'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=$lat,$lng'
    );
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Google Maps қосымшасы табылмады')),
        );
      }
    }
  }

  void _showStreetViewSheet() {
    if (_arPoints.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Проблемалы аймақтар табылмады — жолдар бос!'),
          backgroundColor: Colors.green,
        ),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40, height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Row(
              children: [
                Icon(Icons.streetview, color: Colors.indigo, size: 24),
                SizedBox(width: 8),
                Text('🔍 AR Болжам нүктелері', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
              ],
            ),
            const SizedBox(height: 4),
            Text('Жүйе болжайтын кептеліс нүктелері', style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
            const SizedBox(height: 16),
            ..._arPoints.map((pt) {
              final isCritical = pt['level'] == 'critical';
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: isCritical ? Colors.red.withValues(alpha: 0.08) : Colors.orange.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isCritical ? Colors.red.withValues(alpha: 0.3) : Colors.orange.withValues(alpha: 0.3),
                  ),
                ),
                child: ListTile(
                  leading: Container(
                    width: 44, height: 44,
                    decoration: BoxDecoration(
                      color: isCritical ? Colors.red.withValues(alpha: 0.15) : Colors.orange.withValues(alpha: 0.15),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      isCritical ? Icons.warning_rounded : Icons.speed,
                      color: isCritical ? Colors.red : Colors.orange,
                    ),
                  ),
                  title: Text(
                    pt['segment_name'] ?? 'Белгісіз',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  subtitle: Text(
                    '${pt['message']}',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                  ),
                  trailing: IconButton(
                    icon: const Icon(Icons.streetview, color: Colors.indigo),
                    tooltip: 'Street View ашу',
                    onPressed: () {
                      Navigator.pop(ctx);
                      _openStreetView(
                        (pt['lat'] as num).toDouble(),
                        (pt['lng'] as num).toDouble(),
                      );
                    },
                  ),
                ),
              );
            }),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
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

    // 1. Слой будущего (Future overlay), если включен прогноз
    if (_isForecastMode && _futureSegments.isNotEmpty) {
      for (final seg in _futureSegments) {
        if (seg.points.length < 2) continue;
        final pts = seg.points.map((p) => gmaps.LatLng(p.latitude, p.longitude)).toList();
        final clr = colorByValue(seg.value); // используем общую функцию или _getTrafficColor
        out.add(gmaps.Polyline(
          polylineId: gmaps.PolylineId('future_${seg.id}'),
          points: pts,
          width: 8,
          color: clr.withValues(alpha: 0.55),
          jointType: gmaps.JointType.round,
        ));
      }
    }

    // 2. Основной маршрут
    if (_route != null && _route!.points.length >= 2) {
      final routePts = _route!.points
          .whereType<LatLng>()
          .map((p) => gmaps.LatLng(p.latitude, p.longitude))
          .toList();

      if (_isForecastMode && _multimodalRec != null && _multimodalRec!['recommend_transfer'] == true) {
        // Мультимодальный маршрут (машина -> самокат/пешком)
        final splitIndex = (routePts.length * 0.6).toInt();
        if (splitIndex > 0 && splitIndex < routePts.length) {
          final carPts = routePts.sublist(0, splitIndex + 1);
          final scooterPts = routePts.sublist(splitIndex);

          out.add(gmaps.Polyline(
            polylineId: const gmaps.PolylineId('route_car'),
            points: carPts,
            color: AppColors.primary,
            width: 5,
          ));

          out.add(gmaps.Polyline(
            polylineId: const gmaps.PolylineId('route_scooter'),
            points: scooterPts,
            color: Colors.green,
            width: 4,
            patterns: [gmaps.PatternItem.dash(20), gmaps.PatternItem.gap(10)], // Пунктир
          ));
        } else {
          out.add(gmaps.Polyline(
            polylineId: const gmaps.PolylineId('route'),
            points: routePts,
            color: AppColors.primary,
            width: 6,
          ));
        }
      } else {
        out.add(gmaps.Polyline(
          polylineId: const gmaps.PolylineId('route'),
          points: routePts,
          color: AppColors.primary,
          width: 6,
        ));
      }
    }
    return out;
  }

  Set<gmaps.Marker> _buildMarkers() {
    final Set<gmaps.Marker> out = {};
    if (a != null) {
      out.add(gmaps.Marker(
        markerId: const gmaps.MarkerId('from'),
        position: gmaps.LatLng(a!.latitude, a!.longitude),
        infoWindow: const gmaps.InfoWindow(title: 'Қайдан'),
        icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(
            gmaps.BitmapDescriptor.hueGreen),
      ));
    }
    if (b != null) {
      out.add(gmaps.Marker(
        markerId: const gmaps.MarkerId('to'),
        position: gmaps.LatLng(b!.latitude, b!.longitude),
        infoWindow: const gmaps.InfoWindow(title: 'Қайда'),
        icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(
            gmaps.BitmapDescriptor.hueRed),
      ));
    }
    
    // Маркер пересадки
    if (_isForecastMode && _route != null && _multimodalRec != null && _multimodalRec!['recommend_transfer'] == true) {
      final routePts = _route!.points;
      final splitIndex = (routePts.length * 0.6).toInt();
      if (splitIndex < routePts.length) {
        final pt = routePts[splitIndex];
        out.add(gmaps.Marker(
          markerId: const gmaps.MarkerId('transfer_point'),
          position: gmaps.LatLng(pt.latitude, pt.longitude),
          infoWindow: const gmaps.InfoWindow(title: 'Ауысу: Самокат / Жаяу'),
          icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(gmaps.BitmapDescriptor.hueOrange), // Парковка/Самокат
        ));
      }
    }
    return out;
  }


  void _onMapLongPress(gmaps.LatLng latLng) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40, height: 4,
                decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)),
              ),
            ),
            const SizedBox(height: 16),
            const Row(
              children: [
                Icon(Icons.warning, color: Colors.orangeAccent, size: 28),
                SizedBox(width: 8),
                Text('What-If Симуляция', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
              ],
            ),
            const SizedBox(height: 8),
            Text('Digital Twin: перекрыть данный участок для симуляции?', style: TextStyle(fontSize: 14, color: Colors.grey.shade600)),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text('Болдырмау'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
                    onPressed: () async {
                      Navigator.pop(ctx);
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Внедрение искусственного затора...')));
                      await ApiClient().simulateClosure(latLng.latitude, latLng.longitude, 15);
                      // Перестроим маршрут
                      if (a != null && b != null) {
                        _buildRouteFromGoogle();
                      }
                    },
                    child: const Text('Перекрыть', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final hasRoute = _route != null && _route!.points.length >= 2;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: Stack(
        children: [
          // 1. Full-screen map
          gmaps.GoogleMap(
            initialCameraPosition: _initialCamera(),
            onMapCreated: (c) {
              _mapController = c;
              _updateMapStyle();
            },
            onLongPress: _onMapLongPress,
            polylines: _buildPolylines(),
            markers: _buildMarkers(),
            mapToolbarEnabled: false,
            myLocationButtonEnabled: false,
            zoomControlsEnabled: false,
            trafficEnabled: _byCar,
            padding: EdgeInsets.only(
              top: MediaQuery.of(context).padding.top + 180,
              bottom: hasRoute ? 120 : 40,
            ),
          ),

          // 2. Top solid card
          SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Material(
                color: Theme.of(context).cardColor,
                elevation: 6,
                shadowColor: Colors.black.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(16),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Inputs and Swap Row
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              children: [
                                // From field
                                SizedBox(
                                  height: 40,
                                  child: TextField(
                                    controller: _fromController,
                                    focusNode: _fromFocus,
                                    style: const TextStyle(fontSize: 14),
                                    decoration: InputDecoration(
                                      hintText: 'Қайдан',
                                      prefixIcon: const Icon(Icons.trip_origin_rounded, size: 18, color: AppColors.primary),
                                      prefixIconConstraints: const BoxConstraints(minWidth: 40),
                                      suffixIcon: Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          GestureDetector(
                                            onTap: _useMyLocation,
                                            child: const Padding(
                                              padding: EdgeInsets.symmetric(horizontal: 4),
                                              child: Icon(Icons.my_location_rounded, size: 18, color: AppColors.primary),
                                            ),
                                          ),
                                          GestureDetector(
                                            onTap: () { _fromController.clear(); _clearRoute(); setState(() {}); },
                                            child: const Padding(
                                              padding: EdgeInsets.only(right: 8, left: 4),
                                              child: Icon(Icons.close, size: 16, color: Colors.grey),
                                            ),
                                          ),
                                        ],
                                      ),
                                      suffixIconConstraints: const BoxConstraints(minWidth: 40),
                                      contentPadding: EdgeInsets.zero,
                                      enabledBorder: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(10),
                                        borderSide: BorderSide(color: Theme.of(context).dividerColor.withValues(alpha: 0.3)),
                                      ),
                                      focusedBorder: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(10),
                                        borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
                                      ),
                                    ),
                                    textInputAction: TextInputAction.next,
                                    onChanged: _onFromChanged,
                                    onTap: () => setState(() => _toSuggestions = []),
                                  ),
                                ),
                                const SizedBox(height: 8),
                                // To field
                                SizedBox(
                                  height: 40,
                                  child: TextField(
                                    controller: _toController,
                                    focusNode: _toFocus,
                                    style: const TextStyle(fontSize: 14),
                                    decoration: InputDecoration(
                                      hintText: 'Қайда',
                                      prefixIcon: const Icon(Icons.location_on_rounded, size: 18, color: Colors.redAccent),
                                      prefixIconConstraints: const BoxConstraints(minWidth: 40),
                                      suffixIcon: GestureDetector(
                                        onTap: () { _toController.clear(); _clearRoute(); setState(() {}); },
                                        child: const Padding(
                                          padding: EdgeInsets.only(right: 8),
                                          child: Icon(Icons.close, size: 16, color: Colors.grey),
                                        ),
                                      ),
                                      suffixIconConstraints: const BoxConstraints(minWidth: 40),
                                      contentPadding: EdgeInsets.zero,
                                      enabledBorder: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(10),
                                        borderSide: BorderSide(color: Theme.of(context).dividerColor.withValues(alpha: 0.3)),
                                      ),
                                      focusedBorder: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(10),
                                        borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
                                      ),
                                    ),
                                    textInputAction: TextInputAction.done,
                                    onChanged: _onToChanged,
                                    onSubmitted: (_) => _buildRouteFromAddresses(),
                                    onTap: () => setState(() => _fromSuggestions = []),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          // Swap button
                          InkWell(
                            onTap: _swapAddresses,
                            borderRadius: BorderRadius.circular(10),
                            child: Container(
                              width: 36,
                              height: 36,
                              decoration: BoxDecoration(
                                color: AppColors.primary.withValues(alpha: 0.08),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(Icons.swap_vert_rounded, color: AppColors.primary, size: 20),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      // Bottom row: toggle + chips
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        physics: const BouncingScrollPhysics(),
                        child: Row(
                          children: [
                            Container(
                              height: 32,
                              padding: const EdgeInsets.all(2),
                              decoration: BoxDecoration(
                                border: Border.all(color: Theme.of(context).dividerColor.withValues(alpha: 0.3)),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  _modeChip(Icons.directions_walk_rounded, 'Жаяу', !_byCar, () {
                                    setState(() => _byCar = false);
                                    if (a != null && b != null) _buildRouteFromGoogle();
                                  }),
                                  _modeChip(Icons.directions_car_rounded, 'Көлік', _byCar, () {
                                    setState(() => _byCar = true);
                                    if (a != null && b != null) _buildRouteFromGoogle();
                                  }),
                                ],
                              ),
                            ),
                            const SizedBox(width: 8),
                            if (_byCar)
                              Container(
                                height: 32,
                                padding: const EdgeInsets.all(2),
                                decoration: BoxDecoration(
                                  border: Border.all(color: Theme.of(context).dividerColor.withValues(alpha: 0.3)),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    _modeChip(Icons.flash_on_rounded, 'Тез', !_antiStressMode, () {
                                      setState(() => _antiStressMode = false);
                                      if (a != null && b != null) _buildRouteFromGoogle();
                                    }),
                                    _modeChip(Icons.self_improvement_rounded, 'Анти-Стресс', _antiStressMode, () {
                                      setState(() => _antiStressMode = true);
                                      if (a != null && b != null) _buildRouteFromGoogle();
                                    }),
                                  ],
                                ),
                              ),
                            if (!_byCar)
                              Container(
                                height: 32,
                                padding: const EdgeInsets.all(2),
                                decoration: BoxDecoration(
                                  border: Border.all(color: Theme.of(context).dividerColor.withValues(alpha: 0.3)),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    _modeChip(Icons.accessible_forward_rounded, 'Кедергісіз', _barrierFreeMode, () {
                                      setState(() => _barrierFreeMode = !_barrierFreeMode);
                                      if (a != null && b != null) _buildRouteFromGoogle();
                                    }),
                                  ],
                                ),
                              ),
                            const SizedBox(width: 8),
                            _miniChip(Icons.home_rounded, 'Үй', () => _handleShortcutTap('home')),
                            const SizedBox(width: 8),
                            _miniChip(Icons.work_rounded, 'Жұмыс', () => _handleShortcutTap('work')),
                            if (_route != null) ...[
                              const SizedBox(width: 8),
                              _loadingMultimodal
                                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                  : GestureDetector(
                                      onTap: _fetchForecastAndMultimodal,
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                        decoration: BoxDecoration(
                                          color: Colors.indigo.withValues(alpha: 0.1),
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(color: Colors.indigo.withValues(alpha: 0.3)),
                                        ),
                                        child: Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            const Icon(Icons.auto_awesome, size: 14, color: Colors.indigo),
                                            const SizedBox(width: 4),
                                            Text(
                                              'AI Болжам +20 мин',
                                              style: TextStyle(
                                                fontSize: 12,
                                                fontWeight: FontWeight.w600,
                                                color: Colors.indigo.shade700,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                            ],
                            if (_isForecastMode && _arPoints.isNotEmpty) ...[
                              const SizedBox(width: 8),
                              GestureDetector(
                                onTap: _showStreetViewSheet,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: Colors.teal.withValues(alpha: 0.1),
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: Colors.teal.withValues(alpha: 0.3)),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(Icons.streetview, size: 14, color: Colors.teal),
                                      const SizedBox(width: 4),
                                      Text(
                                        'Street View',
                                        style: TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.w600,
                                          color: Colors.teal.shade700,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                            if (loading) ...[
                              const SizedBox(width: 12),
                              const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // 3. Suggestions (from)
          if (_fromSuggestions.isNotEmpty && _fromFocus.hasFocus)
            Positioned(
              top: MediaQuery.of(context).padding.top + 58,
              left: 12,
              right: 62,
              child: _buildSuggestionsList(_fromSuggestions, _onFromSuggestionTap),
            ),

          // 4. Suggestions (to)
          if (_toSuggestions.isNotEmpty && _toFocus.hasFocus)
            Positioned(
              top: MediaQuery.of(context).padding.top + 106,
              left: 12,
              right: 62,
              child: _buildSuggestionsList(_toSuggestions, _onToSuggestionTap),
            ),

          // 5. Route info (bottom)
          if (hasRoute)
            Positioned(
              left: 12,
              right: 80, // Оставляем место для микрофона справа
              bottom: 104, // Поднимаем над нижним меню
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: BackdropFilter(
                  filter: dart_ui.ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor.withValues(alpha: 0.92),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withValues(alpha: 0.1), blurRadius: 14, offset: const Offset(0, -2)),
                      ],
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(12)),
                          child: const Icon(Icons.route_rounded, color: AppColors.primary, size: 22),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Builder(
                            builder: (context) {
                              final seconds = _route!.durationInTrafficSeconds ?? _route!.durationSeconds;
                              final arrival = DateTime.now().add(Duration(seconds: seconds));
                              final arrText = '${arrival.hour.toString().padLeft(2, '0')}:${arrival.minute.toString().padLeft(2, '0')}-те жетесіз';
                              
                              return Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    _route!.durationInTrafficText ?? _route!.durationText,
                                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 17, color: AppColors.primary),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    _byCar && _route!.durationInTrafficText != null
                                        ? 'Кептеліспен • ${_route!.distanceText ?? ''} • $arrText'
                                        : '${_route!.distanceText ?? ''} • $arrText',
                                    style: TextStyle(fontSize: 12, color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.6)),
                                  ),
                                  if (_parkingData != null && _byCar) ...[
                                    const SizedBox(height: 8),
                                    Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: Colors.blue.withValues(alpha: 0.1),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Row(
                                        children: [
                                          const Icon(Icons.local_parking_rounded, color: Colors.blue, size: 16),
                                          const SizedBox(width: 6),
                                          Expanded(
                                            child: Text(
                                              _parkingData!['message'] ?? 'AI Паркинг: Орындар талданды',
                                              style: const TextStyle(fontSize: 11, color: Colors.blue),
                                            ),
                                          ),
                                        ],
                                      ),
                                    )
                                  ],
                                ],
                              );
                            }
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

          // 6. Error
          if (error != null)
            Positioned(
              left: 14,
              right: 14,
              bottom: hasRoute ? 190 : 110,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Theme.of(context).brightness == Brightness.dark
                      ? Colors.red.shade900.withValues(alpha: 0.8) : Colors.red.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, size: 18, color: Colors.red.shade400),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        error!.replaceFirst('Exception: ', ''),
                        style: TextStyle(fontSize: 12, color: Theme.of(context).brightness == Brightness.dark ? Colors.red.shade200 : Colors.red.shade800),
                      ),
                    ),
                    GestureDetector(
                      onTap: () => setState(() => error = null),
                      child: Icon(Icons.close, size: 16, color: Colors.red.shade300),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _modeChip(IconData icon, String label, bool active, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(
          color: active ? AppColors.primary : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: active ? Colors.white : Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.5)),
            const SizedBox(width: 3),
            Text(label, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: active ? Colors.white : Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.5))),
          ],
        ),
      ),
    );
  }

  Widget _miniChip(IconData icon, String label, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 30,
        padding: const EdgeInsets.symmetric(horizontal: 8),
        decoration: BoxDecoration(
          color: Theme.of(context).scaffoldBackgroundColor.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Theme.of(context).dividerColor.withValues(alpha: 0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 13, color: AppColors.primary),
            const SizedBox(width: 3),
            Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionsList(List<PlacePrediction> suggestions, Function(PlacePrediction) onTap) {
    return Material(
      elevation: 8,
      borderRadius: BorderRadius.circular(12),
      color: Theme.of(context).cardColor,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxHeight: 200),
        child: ListView.separated(
          padding: const EdgeInsets.symmetric(vertical: 4),
          shrinkWrap: true,
          itemCount: suggestions.length,
          separatorBuilder: (_, __) => Divider(height: 1, color: Theme.of(context).dividerColor.withValues(alpha: 0.3)),
          itemBuilder: (context, i) {
            final p = suggestions[i];
            return InkWell(
              onTap: () => onTap(p),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                child: Row(
                  children: [
                    Icon(Icons.place_rounded, size: 18, color: AppColors.primary.withValues(alpha: 0.7)),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(p.description, style: TextStyle(fontSize: 13, color: Theme.of(context).textTheme.bodyLarge?.color), maxLines: 2, overflow: TextOverflow.ellipsis),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
