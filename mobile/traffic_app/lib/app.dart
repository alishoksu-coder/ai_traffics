import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'map_screen.dart';
import 'navigator_screen.dart';

/// Основные цвета приложения (синхрон с темой)
class _AppColors {
  static const primary = Color(0xFF0D7EA7);
  static const primaryDark = Color(0xFF065A82);
  static const surface = Color(0xFFF8FAFC);
  static const surfaceVariant = Color(0xFFE8EEF2);
  static const onSurface = Color(0xFF1E293B);
  static const onSurfaceVariant = Color(0xFF64748B);
  static const outline = Color(0xFFCBD5E1);
}

class TrafficApp extends StatelessWidget {
  const TrafficApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Traffic Monitor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: GoogleFonts.inter().fontFamily,
        textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme),
        primaryTextTheme: GoogleFonts.interTextTheme(ThemeData.light().primaryTextTheme),
        colorScheme: ColorScheme.light(
          primary: _AppColors.primary,
          onPrimary: Colors.white,
          primaryContainer: _AppColors.primary.withOpacity(0.12),
          onPrimaryContainer: _AppColors.primaryDark,
          secondary: const Color(0xFF0EA5E9),
          onSecondary: Colors.white,
          surface: Colors.white,
          onSurface: _AppColors.onSurface,
          surfaceContainerHighest: _AppColors.surfaceVariant,
          onSurfaceVariant: _AppColors.onSurfaceVariant,
          outline: _AppColors.outline,
          error: const Color(0xFFDC2626),
          onError: Colors.white,
        ),
        scaffoldBackgroundColor: _AppColors.surface,
        appBarTheme: AppBarTheme(
          elevation: 0,
          scrolledUnderElevation: 2,
          centerTitle: false,
          backgroundColor: Colors.white,
          foregroundColor: _AppColors.onSurface,
          surfaceTintColor: Colors.transparent,
          titleTextStyle: GoogleFonts.inter(
            color: _AppColors.onSurface,
            fontSize: 20,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.3,
          ),
          iconTheme: const IconThemeData(color: _AppColors.onSurface, size: 24),
        ),
        cardTheme: CardThemeData(
          elevation: 0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          color: Colors.white,
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          clipBehavior: Clip.antiAlias,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: _AppColors.surfaceVariant.withOpacity(0.5),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide(color: _AppColors.outline.withOpacity(0.6)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: _AppColors.primary, width: 2),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          hintStyle: GoogleFonts.inter(color: _AppColors.onSurfaceVariant, fontSize: 15),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: _AppColors.primary,
            foregroundColor: Colors.white,
            elevation: 0,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            textStyle: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 16),
          ),
        ),
        chipTheme: ChipThemeData(
          backgroundColor: _AppColors.surfaceVariant.withOpacity(0.8),
          selectedColor: _AppColors.primary,
          labelStyle: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w500),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        navigationBarTheme: NavigationBarThemeData(
          height: 72,
          elevation: 0,
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          indicatorColor: _AppColors.primary.withOpacity(0.15),
          indicatorShape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          labelTextStyle: MaterialStateProperty.resolveWith((states) {
            if (states.contains(MaterialState.selected)) {
              return GoogleFonts.inter(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: _AppColors.primary,
              );
            }
            return GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: _AppColors.onSurfaceVariant,
            );
          }),
          iconTheme: MaterialStateProperty.resolveWith((states) {
            if (states.contains(MaterialState.selected)) {
              return const IconThemeData(color: _AppColors.primary, size: 24);
            }
            return const IconThemeData(color: _AppColors.onSurfaceVariant, size: 24);
          }),
        ),
        snackBarTheme: SnackBarThemeData(
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          backgroundColor: _AppColors.onSurface,
          contentTextStyle: GoogleFonts.inter(color: Colors.white),
        ),
        dropdownMenuTheme: DropdownMenuThemeData(
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: _AppColors.surfaceVariant.withOpacity(0.5),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          ),
        ),
      ),
      home: const HomeShell(),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = const <Widget>[
      MapScreen(),
      NavigatorScreen(),
    ];

    return Scaffold(
      body: IndexedStack(index: _index, children: pages),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 20,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: NavigationBar(
              selectedIndex: _index,
              onDestinationSelected: (i) => setState(() => _index = i),
              destinations: const [
                NavigationDestination(icon: Icon(Icons.map_outlined), selectedIcon: Icon(Icons.map), label: 'Карта'),
                NavigationDestination(icon: Icon(Icons.navigation_outlined), selectedIcon: Icon(Icons.navigation), label: 'Навигатор'),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
