import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';

import 'config.dart';
import 'models.dart';

/// Декодирует полилинию Google (encoded polyline) в список координат [lat, lng].
List<LatLng> decodePolyline(String encoded) {
  final list = <LatLng>[];
  int index = 0;
  int lat = 0;
  int lng = 0;
  const scale = 1e5;

  while (index < encoded.length) {
    int shift = 0;
    int result = 0;
    int byte;
    do {
      byte = encoded.codeUnitAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);
    final dlat = (result & 1) != 0 ? ~(result >> 1) : (result >> 1);
    lat += dlat;

    shift = 0;
    result = 0;
    do {
      byte = encoded.codeUnitAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);
    final dlng = (result & 1) != 0 ? ~(result >> 1) : (result >> 1);
    lng += dlng;

    list.add(LatLng(lat / scale, lng / scale));
  }
  return list;
}

/// Результат маршрута Google Directions API (оптимальный маршрут с учётом трафика).
class GoogleDirectionsResult {
  final List<LatLng> points;
  final String durationText;
  final int durationSeconds;
  final String? durationInTrafficText;
  final int? durationInTrafficSeconds;
  final String? distanceText;

  const GoogleDirectionsResult({
    required this.points,
    required this.durationText,
    required this.durationSeconds,
    this.durationInTrafficText,
    this.durationInTrafficSeconds,
    this.distanceText,
  });
}

/// Режим передвижения для маршрута.
enum RouteMode { driving, walking }

/// Маршрут от A до B через Google Directions API.
/// [mode] — driving (автомобиль, с учётом трафика) или walking (пешком).
Future<GoogleDirectionsResult> getGoogleDirections({
  required double originLat,
  required double originLng,
  required double destLat,
  required double destLng,
  RouteMode mode = RouteMode.driving,
}) async {
  final origin = '$originLat,$originLng';
  final destination = '$destLat,$destLng';
  final modeStr = mode == RouteMode.walking ? 'walking' : 'driving';
  var url = 'https://maps.googleapis.com/maps/api/directions/json'
      '?origin=${Uri.encodeComponent(origin)}'
      '&destination=${Uri.encodeComponent(destination)}'
      '&mode=$modeStr'
      '&key=$kGoogleMapsApiKey'
      '&language=ru';
  if (mode == RouteMode.driving) {
    url += '&departure_time=now&traffic_model=best_guess';
  }
  final uri = Uri.parse(url);
  final r = await http.get(uri).timeout(const Duration(seconds: 15));
  if (r.statusCode != 200) throw Exception('Directions: HTTP ${r.statusCode}');
  final data = jsonDecode(r.body) as Map<String, dynamic>;
  final status = data['status'] as String?;
  if (status != 'OK') {
    final err = data['error_message'] as String? ?? status ?? 'Unknown';
    throw Exception('Directions: $err');
  }
  final routes = data['routes'] as List?;
  if (routes == null || routes.isEmpty) throw Exception('Маршрут не найден');
  final route = routes[0] as Map<String, dynamic>;
  final overview = route['overview_polyline'] as Map<String, dynamic>?;
  final encoded = overview?['points'] as String?;
  if (encoded == null || encoded.isEmpty) throw Exception('Нет геометрии маршрута');

  final points = decodePolyline(encoded);
  final legs = route['legs'] as List?;
  if (legs == null || legs.isEmpty) throw Exception('Нет данных о маршруте');

  int totalDurationSec = 0;
  int? totalDurationTrafficSec;
  String? durationText;
  String? durationInTrafficText;
  String? distanceText;

  for (final leg in legs) {
    final legMap = leg as Map<String, dynamic>;
    final dur = legMap['duration'] as Map<String, dynamic>?;
    if (dur != null) {
      totalDurationSec += (dur['value'] as num?)?.toInt() ?? 0;
      durationText ??= dur['text'] as String?;
    }
    final durTraffic = legMap['duration_in_traffic'] as Map<String, dynamic>?;
    if (durTraffic != null) {
      final sec = (durTraffic['value'] as num?)?.toInt() ?? 0;
      totalDurationTrafficSec = (totalDurationTrafficSec ?? 0) + sec;
      durationInTrafficText ??= durTraffic['text'] as String?;
    }
    final dist = legMap['distance'] as Map<String, dynamic>?;
    if (dist != null) distanceText ??= dist['text'] as String?;
  }

  if (legs.length > 1) {
    durationText = _formatSeconds(totalDurationSec);
    if (totalDurationTrafficSec != null) {
      durationInTrafficText = _formatSeconds(totalDurationTrafficSec);
    }
  }

  return GoogleDirectionsResult(
    points: points,
    durationText: durationText ?? '—',
    durationSeconds: totalDurationSec,
    durationInTrafficText: durationInTrafficText,
    durationInTrafficSeconds: totalDurationTrafficSec,
    distanceText: distanceText,
  );
}

String _formatSeconds(int sec) {
  if (sec < 60) return '$sec сек';
  final m = sec ~/ 60;
  if (m < 60) return '$m мин';
  final h = m ~/ 60;
  final mm = m % 60;
  if (mm == 0) return '$h ч';
  return '$h ч $mm мин';
}

/// Обратное геокодирование: по координатам возвращает адрес (Google Geocoding API).
Future<String> getAddressForLatLng(double lat, double lng) async {
  final uri = Uri.parse(
    'https://maps.googleapis.com/maps/api/geocode/json'
    '?latlng=$lat,$lng'
    '&key=${kGoogleMapsApiKey}'
    '&language=ru',
  );
  final r = await http.get(uri).timeout(const Duration(seconds: 8));
  if (r.statusCode != 200) throw Exception('Geocoding: HTTP ${r.statusCode}');
  final data = jsonDecode(r.body) as Map<String, dynamic>;
  final status = data['status'] as String?;
  if (status != 'OK') {
    final err = data['error_message'] as String? ?? status ?? 'Unknown';
    throw Exception('Geocoding: $err');
  }
  final results = data['results'] as List?;
  if (results == null || results.isEmpty) return 'Адрес не найден';
  final first = results[0] as Map<String, dynamic>;
  return (first['formatted_address'] as String?) ?? 'Адрес не найден';
}

/// Результат поиска места по запросу (прямое геокодирование).
class PlaceResult {
  final double lat;
  final double lon;
  final String formattedAddress;

  const PlaceResult({required this.lat, required this.lon, required this.formattedAddress});
}

/// Один вариант подсказки адреса (Google Places Autocomplete).
class PlacePrediction {
  final String description;
  final String placeId;

  const PlacePrediction({required this.description, required this.placeId});
}

/// Подсказки адресов по введённому тексту (Google Places Autocomplete).
Future<List<PlacePrediction>> getPlaceAutocomplete(String input) async {
  final q = input.trim();
  if (q.length < 2) return [];
  final uri = Uri.parse(
    'https://maps.googleapis.com/maps/api/place/autocomplete/json'
    '?input=${Uri.encodeComponent(q)}'
    '&key=$kGoogleMapsApiKey'
    '&language=ru',
  );
  final r = await http.get(uri).timeout(const Duration(seconds: 8));
  if (r.statusCode != 200) return [];
  final data = jsonDecode(r.body) as Map<String, dynamic>;
  if (data['status'] != 'OK' && data['status'] != 'ZERO_RESULTS') return [];
  final predictions = data['predictions'] as List?;
  if (predictions == null) return [];
  final list = <PlacePrediction>[];
  for (final p in predictions) {
    final map = p as Map<String, dynamic>;
    final desc = map['description'] as String?;
    final id = map['place_id'] as String?;
    if (desc != null && id != null) list.add(PlacePrediction(description: desc, placeId: id));
  }
  return list;
}

/// Координаты и адрес по place_id (Google Place Details).
Future<PlaceResult> getPlaceDetails(String placeId) async {
  final uri = Uri.parse(
    'https://maps.googleapis.com/maps/api/place/details/json'
    '?place_id=${Uri.encodeComponent(placeId)}'
    '&key=$kGoogleMapsApiKey'
    '&language=ru'
    '&fields=geometry,formatted_address',
  );
  final r = await http.get(uri).timeout(const Duration(seconds: 8));
  if (r.statusCode != 200) throw Exception('Place Details: HTTP ${r.statusCode}');
  final data = jsonDecode(r.body) as Map<String, dynamic>;
  if (data['status'] != 'OK') throw Exception('Место не найдено');
  final result = data['result'] as Map<String, dynamic>?;
  if (result == null) throw Exception('Нет данных');
  final geo = result['geometry'] as Map<String, dynamic>?;
  final loc = geo?['location'] as Map<String, dynamic>?;
  final formatted = result['formatted_address'] as String? ?? '';
  if (loc == null) throw Exception('Координаты не найдены');
  final lat = (loc['lat'] as num).toDouble();
  final lng = (loc['lng'] as num).toDouble();
  return PlaceResult(lat: lat, lon: lng, formattedAddress: formatted);
}

/// Полная информация о месте (кафе, магазин, организация) для карточки.
class PlaceDetailsFull {
  final String name;
  final double? rating;
  final int? userRatingsTotal;
  final List<String> photoUrls;
  final String? openingHoursText;
  final bool? openNow;
  final String? phone;
  final String? website;
  final String address;
  final double lat;
  final double lng;
  final String placeId;

  const PlaceDetailsFull({
    required this.name,
    this.rating,
    this.userRatingsTotal,
    this.photoUrls = const [],
    this.openingHoursText,
    this.openNow,
    this.phone,
    this.website,
    required this.address,
    required this.lat,
    required this.lng,
    required this.placeId,
  });
}

/// Поиск места рядом с точкой (Google Places Nearby Search).
/// Возвращает place_id места, **ближайшего** к (lat, lng), а не по «важности» — чтобы при тапе по разным точкам показывались разные места.
Future<String?> getNearbyPlaceId(double lat, double lng) async {
  final uri = Uri.parse(
    'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    '?location=$lat,$lng'
    '&radius=50'
    '&key=$kGoogleMapsApiKey'
    '&language=ru',
  );
  final r = await http.get(uri).timeout(const Duration(seconds: 8));
  if (r.statusCode != 200) return null;
  final data = jsonDecode(r.body) as Map<String, dynamic>;
  if (data['status'] != 'OK' && data['status'] != 'ZERO_RESULTS') return null;
  final results = data['results'] as List?;
  if (results == null || results.isEmpty) return null;

  const dist = Distance();
  final tap = LatLng(lat, lng);
  String? bestPlaceId;
  double bestMeters = double.infinity;

  for (final item in results) {
    final map = item as Map<String, dynamic>;
    final geo = map['geometry'] as Map<String, dynamic>?;
    final loc = geo?['location'] as Map<String, dynamic>?;
    final placeId = map['place_id'] as String?;
    if (loc == null || placeId == null) continue;
    final placeLat = (loc['lat'] as num).toDouble();
    final placeLng = (loc['lng'] as num).toDouble();
    final meters = dist(tap, LatLng(placeLat, placeLng));
    if (meters < bestMeters) {
      bestMeters = meters;
      bestPlaceId = placeId;
    }
  }
  return bestPlaceId;
}

/// Полные детали места по place_id (название, рейтинг, фото, часы, телефон, сайт, адрес).
Future<PlaceDetailsFull> getPlaceDetailsFull(String placeId) async {
  final fields = 'name,rating,user_ratings_total,formatted_phone_number,website,'
      'formatted_address,opening_hours,photos,geometry';
  final uri = Uri.parse(
    'https://maps.googleapis.com/maps/api/place/details/json'
    '?place_id=${Uri.encodeComponent(placeId)}'
    '&key=$kGoogleMapsApiKey'
    '&language=ru'
    '&fields=$fields',
  );
  final r = await http.get(uri).timeout(const Duration(seconds: 10));
  if (r.statusCode != 200) throw Exception('Place Details: HTTP ${r.statusCode}');
  final data = jsonDecode(r.body) as Map<String, dynamic>;
  if (data['status'] != 'OK') throw Exception('Место не найдено');
  final result = data['result'] as Map<String, dynamic>?;
  if (result == null) throw Exception('Нет данных');

  final name = (result['name'] as String?) ?? 'Место';
  final rating = (result['rating'] as num?)?.toDouble();
  final userRatingsTotal = (result['user_ratings_total'] as num?)?.toInt();
  final address = (result['formatted_address'] as String?) ?? '';
  final phone = result['formatted_phone_number'] as String?;
  final website = result['website'] as String?;

  double lat = 0, lng = 0;
  final geo = result['geometry'] as Map<String, dynamic>?;
  final loc = geo?['location'] as Map<String, dynamic>?;
  if (loc != null) {
    lat = (loc['lat'] as num).toDouble();
    lng = (loc['lng'] as num).toDouble();
  }

  final photosRaw = result['photos'] as List?;
  final photoUrls = <String>[];
  if (photosRaw != null) {
    for (var i = 0; i < photosRaw.length && i < 5; i++) {
      final ref = (photosRaw[i] as Map<String, dynamic>)['photo_reference'] as String?;
      if (ref != null) {
        photoUrls.add(
          'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=${Uri.encodeComponent(ref)}&key=$kGoogleMapsApiKey',
        );
      }
    }
  }

  String? openingHoursText;
  bool? openNow;
  final oh = result['opening_hours'] as Map<String, dynamic>?;
  if (oh != null) {
    openNow = oh['open_now'] as bool?;
    final weekday = oh['weekday_text'] as List?;
    if (weekday != null && weekday.isNotEmpty) {
      openingHoursText = weekday.map((e) => e.toString()).join('\n');
    }
  }

  return PlaceDetailsFull(
    name: name,
    rating: rating,
    userRatingsTotal: userRatingsTotal,
    photoUrls: photoUrls,
    openingHoursText: openingHoursText,
    openNow: openNow,
    phone: phone,
    website: website,
    address: address,
    lat: lat,
    lng: lng,
    placeId: placeId,
  );
}

/// Прямое геокодирование: по тексту запроса (адрес или название места) возвращает координаты.
Future<PlaceResult> getPlaceFromQuery(String query) async {
  final q = query.trim();
  if (q.isEmpty) throw Exception('Введите адрес или название места');
  // Добавляем «Астана» для лучшего результата по городу
  final address = q.contains('Астана') || q.contains('Astana') ? q : '$q, Астана';
  final uri = Uri.parse(
    'https://maps.googleapis.com/maps/api/geocode/json'
    '?address=${Uri.encodeComponent(address)}'
    '&key=${kGoogleMapsApiKey}'
    '&language=ru',
  );
  final r = await http.get(uri).timeout(const Duration(seconds: 10));
  if (r.statusCode != 200) throw Exception('Geocoding: HTTP ${r.statusCode}');
  final data = jsonDecode(r.body) as Map<String, dynamic>;
  final status = data['status'] as String?;
  if (status != 'OK' && status != 'ZERO_RESULTS') {
    final err = data['error_message'] as String? ?? status ?? 'Unknown';
    throw Exception('Geocoding: $err');
  }
  final results = data['results'] as List?;
  if (results == null || results.isEmpty) throw Exception('Место не найдено. Уточните запрос.');
  final first = results[0] as Map<String, dynamic>;
  final geo = first['geometry'] as Map<String, dynamic>?;
  final loc = geo?['location'] as Map<String, dynamic>?;
  if (loc == null) throw Exception('Координаты не найдены');
  final lat = (loc['lat'] as num).toDouble();
  final lng = (loc['lng'] as num).toDouble();
  final formatted = (first['formatted_address'] as String?) ?? '$lat, $lng';
  return PlaceResult(lat: lat, lon: lng, formattedAddress: formatted);
}

class ApiClient {
  final http.Client _http;
  ApiClient({http.Client? httpClient}) : _http = httpClient ?? http.Client();

  Future<List<MapVehicle>> getVehicles() async {
    final uri = Uri.parse('$kApiBaseUrl/vehicles');
    final r = await _http.get(uri).timeout(const Duration(seconds: 10));
    if (r.statusCode != 200) throw Exception('HTTP ${r.statusCode}: ${r.body}');
    final decoded = jsonDecode(r.body);
    final list = decoded is Map ? (decoded['items'] as List? ?? []) : (decoded as List? ?? []);
    return list.map((e) => MapVehicle.fromJson(e is Map ? e as Map<String, dynamic> : Map<String, dynamic>.from(e as Map))).toList();
  }

  Future<List<Friend>> getFriends() async {
    final uri = Uri.parse('$kApiBaseUrl/friends');
    final r = await _http.get(uri).timeout(const Duration(seconds: 10));
    if (r.statusCode != 200) throw Exception('HTTP ${r.statusCode}: ${r.body}');
    final decoded = jsonDecode(r.body);
    final list = decoded is Map ? (decoded['items'] as List? ?? []) : [];
    return list.map((e) => Friend.fromJson(e is Map ? e as Map<String, dynamic> : Map<String, dynamic>.from(e as Map))).toList();
  }

  Future<void> addFriend(String name) async {
    final uri = Uri.parse('$kApiBaseUrl/friends');
    final r = await _http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name}),
    ).timeout(const Duration(seconds: 10));
    if (r.statusCode != 200 && r.statusCode != 201) throw Exception('HTTP ${r.statusCode}: ${r.body}');
  }

  Future<String> adminLogin(String login, String password) async {
    final uri = Uri.parse('$kApiBaseUrl/admin/login');
    final r = await _http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'login': login, 'password': password}),
    ).timeout(const Duration(seconds: 10));
    if (r.statusCode != 200) throw Exception(r.body.isNotEmpty ? r.body : 'Invalid login or password');
    final decoded = jsonDecode(r.body) as Map<String, dynamic>;
    return decoded['token'] as String? ?? '';
  }

  Future<Map<String, dynamic>> adminDashboard(String token) async {
    final uri = Uri.parse('$kApiBaseUrl/admin/dashboard');
    final r = await _http.get(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    ).timeout(const Duration(seconds: 10));
    if (r.statusCode != 200) throw Exception('HTTP ${r.statusCode}: ${r.body}');
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  Future<List<RoadSegment>> getRoadSegments(int horizon) async {
    final uri = Uri.parse('$kApiBaseUrl/roads/segments?horizon=$horizon');

    final r = await _http.get(uri).timeout(const Duration(seconds: 15));
    if (r.statusCode != 200) {
      throw Exception('HTTP ${r.statusCode}: ${r.body}');
    }

    final decoded = jsonDecode(r.body);
    print('DEBUG: API response type: ${decoded.runtimeType}');
    if (decoded is Map) {
      print('DEBUG: API response keys: ${decoded.keys}');
      print('DEBUG: items count: ${decoded['items']?.length ?? 0}');
    }

    // поддержим 2 формата: либо список, либо объект {segments:[...]}
    final List items;
    if (decoded is List) {
      items = decoded;
    } else if (decoded is Map<String, dynamic>) {
      final x = decoded['segments'] ?? decoded['items'] ?? decoded['data'];
      if (x is List) {
        items = x;
      } else {
        throw Exception('Bad response: expected list in segments/items/data');
      }
    } else {
      throw Exception('Bad response: expected JSON list or object');
    }

    final out = <RoadSegment>[];
    for (final e in items) {
      if (e is Map<String, dynamic>) {
        out.add(RoadSegment.fromJson(e));
      } else if (e is Map) {
        out.add(RoadSegment.fromJson(e.cast<String, dynamic>()));
      }
    }
    return out;
  }
}
