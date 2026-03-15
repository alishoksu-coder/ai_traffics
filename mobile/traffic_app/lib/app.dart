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

class _AppColors {
  static const primary = Color(0xFF0D7EA7);
  static const primaryDark = Color(0xFF065A82);
}

class TrafficApp extends StatelessWidget {
  const TrafficApp({super.key});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: ThemeNotifier(),
      builder: (context, _) {
        final isDark = ThemeNotifier().isDarkMode;

        return MaterialApp(
          title: 'AI Traffic Monitor',
          debugShowCheckedModeBanner: false,
          themeMode: isDark ? ThemeMode.dark : ThemeMode.light,
          theme: _buildTheme(Brightness.light),
          darkTheme: _buildTheme(Brightness.dark),
          home: const SplashScreen(nextScreen: HomeShell()),
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
        surface: isDark ? const Color(0xFF0F172A) : const Color(0xFFF8FAFC),
      ),
      scaffoldBackgroundColor:
          isDark ? const Color(0xFF0F172A) : const Color(0xFFF8FAFC),
      appBarTheme: AppBarTheme(
        elevation: 0,
        backgroundColor: isDark ? const Color(0xFF1E293B) : Colors.white,
        foregroundColor: isDark ? Colors.white : const Color(0xFF1E293B),
        centerTitle: false,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: isDark ? Colors.white : const Color(0xFF1E293B),
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: isDark ? const Color(0xFF1E293B) : Colors.white,
        indicatorColor: _AppColors.primary.withOpacity(0.2),
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
      label: 'Навигатор',
    ),
    _TabConfig(
      icon: Icons.route_outlined,
      activeIcon: Icons.route_rounded,
      label: 'Маршруты',
    ),
    _TabConfig(
      icon: Icons.lightbulb_outline_rounded,
      activeIcon: Icons.lightbulb_rounded,
      label: 'AI Советы',
    ),
    _TabConfig(
      icon: Icons.grid_view_outlined,
      activeIcon: Icons.grid_view_rounded,
      label: 'Ещё',
    ),
  ];

  @override
  void initState() {
    super.initState();
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

  @override
  void dispose() {
    _pageController.dispose();
    _fabAnimController.dispose();
    super.dispose();
  }

  void _onTabSelected(int i) {
    if (i == _index) return;
    setState(() => _index = i);
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
      _fabAnimController.reset();
      _fabAnimController.forward();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
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
      floatingActionButton: (_index == 0 || _index == 1)
          ? ScaleTransition(
              scale: _fabScale,
              child: FloatingActionButton(
                heroTag: 'voice_fab',
                onPressed: () {
                  showVoiceQuerySheet(context, onResult: (result) {
                    // Переключаемся на Навигатор после выбора маршрута
                    _onTabSelected(1);
                  });
                },
                backgroundColor: AppColors.primary,
                elevation: 6,
                child: const Icon(Icons.mic_rounded, color: Colors.white, size: 26),
              ),
            )
          : null,

      // ─── Bottom Navigation Bar ───
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(isDark ? 0.3 : 0.06),
              blurRadius: 20,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: NavigationBar(
          selectedIndex: _index,
          onDestinationSelected: _onTabSelected,
          animationDuration: const Duration(milliseconds: 400),
          destinations: _tabs
              .map((t) => NavigationDestination(
                    icon: Icon(t.icon),
                    selectedIcon: _AnimatedNavIcon(icon: t.activeIcon),
                    label: t.label,
                  ))
              .toList(),
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

/// Анимированная иконка для выбранной вкладки —
/// при переключении делает bounce + scale эффект.
class _AnimatedNavIcon extends StatefulWidget {
  final IconData icon;
  const _AnimatedNavIcon({required this.icon});

  @override
  State<_AnimatedNavIcon> createState() => _AnimatedNavIconState();
}

class _AnimatedNavIconState extends State<_AnimatedNavIcon>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _scale = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.25), weight: 40),
      TweenSequenceItem(tween: Tween(begin: 1.25, end: 0.95), weight: 30),
      TweenSequenceItem(tween: Tween(begin: 0.95, end: 1.0), weight: 30),
    ]).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scale,
      child: Icon(widget.icon),
    );
  }
}
