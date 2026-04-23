import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'map_screen.dart';
import 'navigator_screen.dart';
import 'drive_screen.dart';
import 'tips_screen.dart';
import 'more_screen.dart';
import 'splash_screen.dart';
import 'theme_notifier.dart';
import 'voice_query_sheet.dart';
import 'common.dart';
import 'auth_wrapper.dart';

class _AppColors {
  static const primary = Color(0xFF007AFF);
}

class TrafficApp extends StatelessWidget {
  const TrafficApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: ThemeNotifier(),
      builder: (context, _) {
        final themeMode = ThemeNotifier().themeMode;

        return MaterialApp(
          title: 'AI Traffic Monitor',
          debugShowCheckedModeBanner: false,
          themeMode: themeMode,
          theme: _buildTheme(Brightness.light),
          darkTheme: _buildTheme(Brightness.dark),
          home: const SplashScreen(nextScreen: AuthWrapper(child: HomeShell())),
        );
      },
    );
  }

  ThemeData _buildTheme(Brightness brightness) {
    final isDark = brightness == Brightness.dark;

    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      fontFamily: GoogleFonts.inter().fontFamily,
      colorScheme: ColorScheme.fromSeed(
        seedColor: _AppColors.primary,
        brightness: brightness,
        surface: isDark ? const Color(0xFF000000) : const Color(0xFFF5F5F7), // Apple dark mode surface
      ),
      scaffoldBackgroundColor:
          isDark ? const Color(0xFF000000) : const Color(0xFFF5F5F7),
      appBarTheme: AppBarTheme(
        elevation: 0,
        backgroundColor: isDark ? const Color(0xCC000000) : const Color(0xCCF5F5F7), // Transparent for glass if extended
        foregroundColor: isDark ? Colors.white : const Color(0xFF1D1D1F),
        centerTitle: false,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.5,
          color: isDark ? Colors.white : const Color(0xFF1D1D1F),
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: isDark ? const Color(0xFF1C1C1E) : Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),
      textTheme: GoogleFonts.interTextTheme().apply(
        bodyColor: isDark ? const Color(0xFFFFFFFF) : const Color(0xFF1D1D1F),
        displayColor: isDark ? const Color(0xFFFFFFFF) : const Color(0xFF1D1D1F),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: isDark ? const Color(0xFF1E293B) : Colors.white,
        indicatorColor: _AppColors.primary.withValues(alpha: 0.2),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final color = states.contains(WidgetState.selected)
              ? _AppColors.primary
              : (isDark ? Colors.white70 : Colors.black54);
          return GoogleFonts.inter(
              fontSize: 12, fontWeight: FontWeight.w600, color: color);
        }),
      ),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> with TickerProviderStateMixin {
  int _index = 0;
  late final PageController _pageController;
  late final AnimationController _fabAnimController;
  late final Animation<double> _fabScale;

  // Конфигурация вкладок
  static const _tabs = <_TabConfig>[
    _TabConfig(
      icon: Icons.map_outlined,
      activeIcon: Icons.map_rounded,
      label: 'Карта',
    ),
    _TabConfig(
      icon: Icons.navigation_outlined,
      activeIcon: Icons.navigation_rounded,
      label: 'Бағдарлау',
    ),
    _TabConfig(
      icon: Icons.route_outlined,
      activeIcon: Icons.route_rounded,
      label: 'Маршруттар',
    ),
    _TabConfig(
      icon: Icons.lightbulb_outline_rounded,
      activeIcon: Icons.lightbulb_rounded,
      label: 'AI Кеңестері',
    ),
    _TabConfig(
      icon: Icons.grid_view_outlined,
      activeIcon: Icons.grid_view_rounded,
      label: 'Қосымша',
    ),
  ];

  @override
  void initState() {
    super.initState();
    globalTabIndex.addListener(_onGlobalTabChanged);
    _pageController = PageController(initialPage: _index);
    _fabAnimController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _fabScale = CurvedAnimation(
      parent: _fabAnimController,
      curve: Curves.easeOutBack,
    );
    _fabAnimController.forward();
  }

  void _onGlobalTabChanged() {
    if (globalTabIndex.value != _index) {
      _onTabSelected(globalTabIndex.value);
    }
  }

  @override
  void dispose() {
    globalTabIndex.removeListener(_onGlobalTabChanged);
    _pageController.dispose();
    _fabAnimController.dispose();
    super.dispose();
  }

  void _onTabSelected(int i) {
    if (i == _index) return;
    setState(() => _index = i);
    globalTabIndex.value = i;
    _pageController.animateToPage(
      i,
      duration: const Duration(milliseconds: 350),
      curve: Curves.easeInOutCubic,
    );
    // Bounce FAB
    _fabAnimController.reset();
    _fabAnimController.forward();
  }

  void _onPageChanged(int page) {
    if (page != _index) {
      setState(() => _index = page);
      globalTabIndex.value = page;
      _fabAnimController.reset();
      _fabAnimController.forward();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      extendBody: true, // Позволяет контенту (особенно карте) быть под навигацией
      body: PageView(
        controller: _pageController,
        onPageChanged: _onPageChanged,
        physics: const NeverScrollableScrollPhysics(),
        children: const [
          MapScreen(),
          NavigatorScreen(),
          DriveScreen(),
          TipsScreen(),
          MoreScreen(),
        ],
      ),

      // ─── Floating Action Button: Голосовой запрос ───
      floatingActionButton: (_index == 1)
          ? ScaleTransition(
              scale: _fabScale,
              child: FloatingActionButton(
                heroTag: 'voice_fab',
                onPressed: () {
                  showVoiceQuerySheet(context, onResult: (result) {
                    _onTabSelected(1);
                  });
                },
                backgroundColor: AppColors.primary,
                elevation: 6,
                child: const Icon(Icons.mic_rounded, color: Colors.white, size: 26),
              ),
            )
          : null,

      // ─── Bottom Navigation Bar (Glass style) ───
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
          child: Container(
            height: 64,
            decoration: BoxDecoration(
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: isDark ? 0.3 : 0.08),
                  blurRadius: 24,
                  offset: const Offset(0, 8),
                ),
              ],
              borderRadius: BorderRadius.circular(32),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(32),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
                child: Container(
                  color: isDark ? const Color(0xFF1C1C1E).withValues(alpha: 0.7) : Colors.white.withValues(alpha: 0.75),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: List.generate(_tabs.length, (i) {
                      final isSelected = _index == i;
                      final t = _tabs[i];
                      return GestureDetector(
                        onTap: () => _onTabSelected(i),
                        behavior: HitTestBehavior.opaque,
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeOutExpo,
                          padding: isSelected 
                              ? const EdgeInsets.symmetric(horizontal: 14, vertical: 10)
                              : const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                          decoration: BoxDecoration(
                            color: isSelected ? AppColors.primary.withValues(alpha: 0.12) : Colors.transparent,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                isSelected ? t.activeIcon : t.icon, 
                                color: isSelected ? AppColors.primary : (isDark ? Colors.white54 : const Color(0xFF86868B)),
                                size: 24,
                              ),
                              if (isSelected)
                                Padding(
                                  padding: const EdgeInsets.only(left: 6),
                                  child: Text(
                                    t.label,
                                    style: const TextStyle(
                                      color: AppColors.primary,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      );
                    }),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Конфигурация одной вкладки
class _TabConfig {
  final IconData icon;
  final IconData activeIcon;
  final String label;

  const _TabConfig({
    required this.icon,
    required this.activeIcon,
    required this.label,
  });
}
