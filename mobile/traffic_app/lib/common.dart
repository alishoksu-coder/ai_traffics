import 'dart:ui' as ui;
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class GlobalRouteRequest {
  final String destinationName;
  final double destinationLat;
  final double destinationLng;
  GlobalRouteRequest({
    required this.destinationName,
    required this.destinationLat,
    required this.destinationLng,
  });
}

final ValueNotifier<GlobalRouteRequest?> globalRouteRequest = ValueNotifier(null);
final ValueNotifier<int> globalTabIndex = ValueNotifier(0);

/// Палитра приложения (карты трафика, кнопки, карточки)
class AppColors {
  static const primary = Color(0xFF007AFF); // Apple Blue
  static const primaryDark = Color(0xFF0056B3);
  static const textPrimary = Color(0xFF1D1D1F); // Apple Gray
  static const textSecondary = Color(0xFF86868B);
  static const background = Color(0xFFF5F5F7); // Apple Background
  static const cardBackground = Colors.white;
  static const divider = Color(0xFFE5E5EA);
  static const surfaceVariant = Color(0xFFF2F2F7);
}

AppBar whiteAppBar(String title, {Widget? trailing, List<Widget>? actions}) {
  return AppBar(
    title: Text(title),
    backgroundColor: Colors.transparent, // Let themed Scaffold/AppBar handle it
    surfaceTintColor: Colors.transparent,
    elevation: 0,
    actions: actions ?? (trailing != null ? [trailing] : null),
  );
}

/// Карточка в едином стиле: скругление, лёгкая тень
BoxDecoration cardDecoration(BuildContext context) {
  final isDark = Theme.of(context).brightness == Brightness.dark;
  return BoxDecoration(
    color: Theme.of(context).cardColor,
    borderRadius: BorderRadius.circular(20), // Softer rounding
    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(isDark ? 0.4 : 0.04), // Elegant subtle shadow
        blurRadius: 24,
        offset: const Offset(0, 8),
      ),
    ],
  );
}

/// value (0..100): зелёный → жёлтый → красный (трафик)
Color colorByValue(double? v) {
  if (v == null) return AppColors.textSecondary;
  final x = v.clamp(0.0, 100.0).toDouble();

  if (x <= 30) {
    return const Color(0xFF22C55E);
  }
  if (x <= 60) {
    final t = (x - 30) / 30.0;
    return Color.lerp(const Color(0xFFEAB308), const Color(0xFFF97316), t)!;
  }
  final t = (x - 60) / 40.0;
  return Color.lerp(const Color(0xFFEF4444), const Color(0xFFB91C1C), t)!;
}

/// value (0..100): примерная скорость км/ч
double speedKmhByValue(double? v) {
  if (v == null) return 45;
  final x = v.clamp(0.0, 100.0).toDouble();
  final speed = 60.0 - 50.0 * (x / 100.0);
  return speed.clamp(8.0, 60.0);
}


/// Generates a premium circular marker with a custom icon/text

Future<BitmapDescriptor> createModernMarker({
  required String text, 
  required Color bgColor,
  bool isSquare = false,
}) async {
  final ui.PictureRecorder pictureRecorder = ui.PictureRecorder();
  final Canvas canvas = Canvas(pictureRecorder);
  
  const double size = 110;
  
  // Shadow
  final Paint shadowPaint = Paint()
    ..color = Colors.black.withOpacity(0.3)
    ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8);
  
  if (isSquare) {
    // Soft rounded square for parking
    final RRect rrect = RRect.fromRectAndRadius(
        const Rect.fromLTWH(5, 5, size - 10, size - 10), const Radius.circular(24));
    canvas.drawRRect(rrect.shift(const Offset(0, 4)), shadowPaint);
    
    // Background
    final Paint bgPaint = Paint()..color = bgColor;
    canvas.drawRRect(rrect, bgPaint);
    
    // Border
    final Paint borderPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 6.0;
    canvas.drawRRect(rrect, borderPaint);
  } else {
    // Circular marker for friends and user
    canvas.drawCircle(const Offset(size/2, size/2 + 4), size/2 - 8, shadowPaint);
    
    final Paint bgPaint = Paint()..color = bgColor;
    canvas.drawCircle(const Offset(size/2, size/2), size/2 - 8, bgPaint);
    
    final Paint borderPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 6.0;
    canvas.drawCircle(const Offset(size/2, size/2), size/2 - 8, borderPaint);
  }
  
  // Draw text
  final TextPainter textPainter = TextPainter(textDirection: TextDirection.ltr);
  textPainter.text = TextSpan(
    text: text,
    style: const TextStyle(
      fontSize: 48, 
      color: Colors.white, 
      fontWeight: FontWeight.w900,
      fontFamily: 'Inter',
    ),
  );
  textPainter.layout();
  textPainter.paint(
    canvas,
    Offset((size - textPainter.width) / 2, (size - textPainter.height) / 2),
  );
  
  final ui.Image image = await pictureRecorder.endRecording().toImage(size.toInt(), size.toInt());
  final ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
  if (byteData == null) return BitmapDescriptor.defaultMarker;
  return BitmapDescriptor.fromBytes(byteData.buffer.asUint8List());
}
