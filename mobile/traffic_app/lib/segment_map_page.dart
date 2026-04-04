import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;
import 'package:latlong2/latlong.dart';

import 'models.dart';
import 'package:traffic_app/common.dart';

class SegmentMapPage extends StatelessWidget {
  final RoadSegment segment;
  const SegmentMapPage({super.key, required this.segment});

  @override
  Widget build(BuildContext context) {
    // Центр — первая точка сегмента
    final first = segment.points.first;
    final center = gmaps.LatLng(first.latitude, first.longitude);

    // Полилиния сегмента (конвертируем latlong2 → google_maps)
    final gPoints = segment.points
        .map((p) => gmaps.LatLng(p.latitude, p.longitude))
        .toList();

    final color = colorByValue(segment.value);

    final polylines = <gmaps.Polyline>{
      gmaps.Polyline(
        polylineId: const gmaps.PolylineId('shadow'),
        points: gPoints,
        width: 10,
        color: Colors.black.withOpacity(0.20),
        jointType: gmaps.JointType.round,
      ),
      gmaps.Polyline(
        polylineId: const gmaps.PolylineId('segment'),
        points: gPoints,
        width: 7,
        color: color.withOpacity(0.95),
        jointType: gmaps.JointType.round,
      ),
    };

    return Scaffold(
      appBar: whiteAppBar('Сегмент ${segment.id}'),
      body: gmaps.GoogleMap(
        initialCameraPosition: gmaps.CameraPosition(
          target: center,
          zoom: 14,
        ),
        polylines: polylines,
        myLocationButtonEnabled: false,
        zoomControlsEnabled: true,
        trafficEnabled: true,
      ),
    );
  }
}
