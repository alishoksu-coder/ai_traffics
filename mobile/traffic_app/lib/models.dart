import 'package:latlong2/latlong.dart';

class RoadSegment {
  final int id;
  final int locationId;
  final String name;
  final String locationName;
  final double? value;
  final List<LatLng> points;

  const RoadSegment({
    required this.id,
    required this.locationId,
    required this.name,
    this.locationName = '',
    required this.value,
    required this.points,
  });

  factory RoadSegment.fromJson(Map<String, dynamic> json) {
    final id = (json['id'] as num?)?.toInt() ?? 0;

    final locRaw = json['location_id'] ?? json['locationId'] ?? 0;
    final locationId = (locRaw as num).toInt();

    final name = (json['name'] ?? '').toString();
    final locName = (json['location_name'] ?? '').toString();

    final v = json['value'];
    final value = v == null ? null : (v as num).toDouble();

    final rawPts =
        (json['points'] ?? json['polyline'] ?? json['coords']) as List? ??
            const [];
    final pts = <LatLng>[];

    for (final p in rawPts) {
      if (p is List && p.length >= 2) {
        var a = (p[0] as num).toDouble();
        var b = (p[1] as num).toDouble();

        // страховка: если вдруг прилетает [lon,lat]
        double lat = a, lon = b;
        if (lat.abs() > 90 && lon.abs() <= 90) {
          lat = b;
          lon = a;
        }
        pts.add(LatLng(lat, lon));
      } else if (p is Map) {
        final m = p.cast<String, dynamic>();
        final lat = (m['lat'] ?? m['latitude']) as num;
        final lon = (m['lon'] ?? m['lng'] ?? m['longitude']) as num;
        pts.add(LatLng(lat.toDouble(), lon.toDouble()));
      }
    }

    return RoadSegment(
      id: id,
      locationId: locationId,
      name: name.isNotEmpty ? name : locName,
      locationName: locName,
      value: value,
      points: pts,
    );
  }
}

/// Транспорт на карте: автобус или машина
class MapVehicle {
  final int id;
  final String type; // 'bus' | 'car'
  final double lat;
  final double lon;
  final String routeName;

  const MapVehicle({
    required this.id,
    required this.type,
    required this.lat,
    required this.lon,
    required this.routeName,
  });

  factory MapVehicle.fromJson(Map<String, dynamic> json) {
    return MapVehicle(
      id: (json['id'] as num?)?.toInt() ?? 0,
      type: (json['type'] ?? 'car').toString(),
      lat: (json['lat'] as num?)?.toDouble() ?? 0,
      lon: (json['lon'] as num?)?.toDouble() ?? 0,
      routeName: (json['route_name'] ?? '').toString(),
    );
  }
}

/// Друг в списке и на карте
class Friend {
  final int id;
  final String name;
  final double? lat;
  final double? lon;
  final int? updatedAt;

  const Friend({
    required this.id,
    required this.name,
    this.lat,
    this.lon,
    this.updatedAt,
  });

  factory Friend.fromJson(Map<String, dynamic> json) {
    final lat = json['lat'];
    final lon = json['lon'];
    return Friend(
      id: (json['id'] as num?)?.toInt() ?? 0,
      name: (json['name'] ?? '').toString(),
      lat: lat != null ? (lat as num).toDouble() : null,
      lon: lon != null ? (lon as num).toDouble() : null,
      updatedAt: (json['updated_at'] as num?)?.toInt(),
    );
  }
}

class TrafficMetrics {
  final int globalScore;
  final String level;
  final String description;

  const TrafficMetrics({
    required this.globalScore,
    required this.level,
    required this.description,
  });

  factory TrafficMetrics.fromJson(Map<String, dynamic> json) {
    return TrafficMetrics(
      globalScore: (json['global_score'] as num?)?.toInt() ?? 0,
      level: (json['level'] ?? '').toString(),
      description: (json['description'] ?? '').toString(),
    );
  }
}
