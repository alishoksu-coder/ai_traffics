import 'package:flutter/material.dart';

/// Палитра приложения (карты трафика, кнопки, карточки)
class AppColors {
  static const primary = Color(0xFF0D7EA7);
  static const primaryDark = Color(0xFF065A82);
  static const textPrimary = Color(0xFF1E293B);
  static const textSecondary = Color(0xFF64748B);
  static const background = Color(0xFFF8FAFC);
  static const cardBackground = Colors.white;
  static const divider = Color(0xFFE2E8F0);
  static const surfaceVariant = Color(0xFFE8EEF2);
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
    borderRadius: BorderRadius.circular(16),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(isDark ? 0.2 : 0.05),
        blurRadius: 12,
        offset: const Offset(0, 4),
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
