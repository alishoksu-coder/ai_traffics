import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../models.dart';
import 'package:traffic_app/common.dart';

class SegmentMapPage extends StatelessWidget {
  final RoadSegment segment;
  const SegmentMapPage({super.key, required this.segment});

  @override
  Widget build(BuildContext context) {
    final LatLng center = segment.points.first;

    return Scaffold(
      appBar: whiteAppBar('Сегмент ${segment.id}'),
      body: FlutterMap(
        options: MapOptions(initialCenter: center, initialZoom: 14),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.example.traffic_app',
          ),
          PolylineLayer(
            polylines: [
              Polyline(
                  points: segment.points,
                  strokeWidth: 10,
                  color: Colors.black.withValues(alpha: 0.20)),
              Polyline(
                  points: segment.points,
                  strokeWidth: 8,
                  color: colorByValue(segment.value).withValues(alpha: 0.95)),
            ],
          ),
        ],
      ),
    );
  }
}
