import 'package:flutter/material.dart';

import 'admin_login_screen.dart';
import 'friends_screen.dart';
import 'metrics_screen.dart';
import 'theme_notifier.dart';
import 'common.dart';
import 'auth_screen.dart';
import 'security_settings_screen.dart';

/// Экран «Ещё» — доступ ко всем второстепенным разделам приложения.
class MoreScreen extends StatelessWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final purpleColor = const Color(0xFF4C45E5);

    return Scaffold(
      backgroundColor: purpleColor, // Оставляем Scaffold фиолетовым для однородности верхней части
      body: Column(
        children: [
          // Фиолетовая шапка
          Container(
            padding: EdgeInsets.only(
              top: MediaQuery.of(context).padding.top + 16,
              left: 24,
              right: 24,
              bottom: 40,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Қосымша',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Профиль және баптаулар',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.white.withOpacity(0.8),
                      ),
                    ),
                  ],
                ),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: IconButton(
                    icon: Icon(isDark ? Icons.wb_sunny_rounded : Icons.nights_stay_rounded, color: Colors.white),
                    onPressed: () => ThemeNotifier().toggleTheme(),
                    tooltip: isDark ? 'Ашық тема' : 'Қараңғы тема',
                  ),
                ),
              ],
            ),
          ),
          
          // Тело с карточками, теперь на белом/тёмном фоне со скруглением!
          Expanded(
            child: Container(
              // Сдвигаем визуально не нужно, скругление само создаст нужный эффект
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF0F172A) : const Color(0xFFF4F7FA), // Цвет фона списка
                borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
              ),
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(20, 32, 20, 100), // Даем отступ сверху внутри белого блока
                  physics: const BouncingScrollPhysics(),
                  children: [
                    // ── Основное ──
                    _SectionHeader(title: 'НЕГІЗГІ'),
                    const SizedBox(height: 12),
                  _MenuCard(
                    children: [
                      _MenuItem(
                        icon: Icons.people_rounded,
                        iconColor: const Color(0xFF8B5CF6),
                        title: 'Достар',
                        subtitle: 'Достар тізімі мен картасы',
                        onTap: () => Navigator.push(context, _buildPageRoute(FriendsScreen(
                          onShowOnMap: () {
                            Navigator.pop(context);
                            globalTabIndex.value = 0;
                          },
                        ))),
                      ),
                      _MenuDivider(),
                      _MenuItem(
                        icon: Icons.psychology_rounded,
                        iconColor: const Color(0xFF0EA5E9),
                        title: 'AI Аналитикасы',
                        subtitle: 'Модель болжамдарының дәлдігі',
                        onTap: () => Navigator.push(context, _buildPageRoute(const MetricsScreen())),
                      ),
                    ],
                  ),
        
                  const SizedBox(height: 28),
                  // ── Управление ──
                  _SectionHeader(title: 'БАСҚАРУ'),
                  const SizedBox(height: 12),
                  _MenuCard(
                    children: [
                      _MenuItem(
                        icon: Icons.admin_panel_settings_rounded,
                        iconColor: const Color(0xFFF59E0B),
                        title: 'Админ-панель',
                        subtitle: 'Жүйе баптаулары',
                        onTap: () => Navigator.push(context, _buildPageRoute(const AdminLoginScreen())),
                      ),
                      _MenuDivider(),
                      _MenuItem(
                        icon: Icons.shield_rounded,
                        iconColor: const Color(0xFF10B981),
                        title: 'Киберқауіпсіздік',
                        subtitle: 'FaceID, TouchID және PIN-кодтар',
                        onTap: () => Navigator.push(context, _buildPageRoute(const SecuritySettingsScreen())),
                      ),
                    ],
                  ),
        
                  const SizedBox(height: 28),
                  // ── Аккаунт ──
                  _SectionHeader(title: 'АККАУНТ'),
                  const SizedBox(height: 12),
                  _MenuCard(
                    children: [
                      _MenuItem(
                        icon: Icons.account_circle_rounded,
                        iconColor: const Color(0xFF6366F1),
                        title: 'Жүйеге кіру',
                        subtitle: 'Синхрондау үшін авторизациядан өтіңіз',
                        onTap: () {
                          Navigator.push(context, _buildPageRoute(const AuthScreen()));
                        },
                      ),
                    ],
                  ),

                  const SizedBox(height: 28),
                  // ── Внешний вид ──
                  _SectionHeader(title: 'СЫРТҚЫ ТҮРІ'),
                  const SizedBox(height: 16),
                  Center(
                    child: AnimatedBuilder(
                      animation: ThemeNotifier(),
                      builder: (context, _) => const NeumorphicThemeToggle(),
                    ),
                  ),
        
                  const SizedBox(height: 48),
                  // ── Версия ──
                  Center(
                    child: Column(
                      children: [
                        Text(
                          'Traffic AI',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.4)),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'v0.1.0 • Astana',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.3)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        ],
      ),
    );
  }
}
/// Заголовок секции
class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 8),
      child: Text(
        title.toUpperCase(),
        style: TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w800,
          letterSpacing: 1.5,
          color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.4),
        ),
      ),
    );
  }
}

/// Карточка-контейнер для группы пунктов меню
class _MenuCard extends StatelessWidget {
  final List<Widget> children;
  const _MenuCard({required this.children});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark ? Colors.white.withOpacity(0.08) : Colors.black.withOpacity(0.06),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(isDark ? 0.2 : 0.05),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(children: children),
    );
  }
}

/// Разделитель внутри _MenuCard
class _MenuDivider extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Divider(
      height: 1,
      thickness: 1,
      indent: 64,
      color: Theme.of(context).dividerColor.withOpacity(0.5),
    );
  }
}

/// Пункт меню с иконкой, заголовком, подзаголовком и стрелкой
class _MenuItem extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;
  final Widget? trailing;
  final VoidCallback onTap;

  const _MenuItem({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    this.trailing,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: iconColor, size: 22),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: Theme.of(context).textTheme.bodyLarge?.color,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.55),
                      ),
                    ),
                  ],
                ),
              ),
              trailing ??
                  Icon(
                    Icons.chevron_right_rounded,
                    color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.3),
                    size: 22,
                  ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Анимированный PageRoute с плавным slide+fade
PageRoute<T> _buildPageRoute<T>(Widget page) {
  return PageRouteBuilder<T>(
    pageBuilder: (context, animation, secondaryAnimation) => page,
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      final curved = CurvedAnimation(parent: animation, curve: Curves.easeOutCubic);
      return SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0.08, 0),
          end: Offset.zero,
        ).animate(curved),
        child: FadeTransition(
          opacity: curved,
          child: child,
        ),
      );
    },
    transitionDuration: const Duration(milliseconds: 350),
  );
}

class NeumorphicThemeToggle extends StatelessWidget {
  const NeumorphicThemeToggle({super.key});

  @override
  Widget build(BuildContext context) {
    final themeMode = ThemeNotifier().themeMode;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    int selectedIndex = 0; // 0 = Light, 1 = Dark, 2 = System
    if (themeMode == ThemeMode.dark) selectedIndex = 1;
    if (themeMode == ThemeMode.system) selectedIndex = 2;

    const double width = 240.0;
    const double height = 64.0;
    const double padding = 6.0;
    final double itemWidth = (width - padding * 2) / 3;

    return Container(
      width: width,
      height: height,
      padding: const EdgeInsets.all(padding),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0), 
        borderRadius: BorderRadius.circular(40),
        boxShadow: isDark
            ? [
                const BoxShadow(color: Colors.black26, offset: Offset(2, 2), blurRadius: 4, blurStyle: BlurStyle.inner),
                const BoxShadow(color: Colors.white10, offset: Offset(-2, -2), blurRadius: 4, blurStyle: BlurStyle.inner),
              ]
            : [
                const BoxShadow(color: Colors.black12, offset: Offset(2, 2), blurRadius: 4, blurStyle: BlurStyle.inner),
                const BoxShadow(color: Colors.white, offset: Offset(-2, -2), blurRadius: 4, blurStyle: BlurStyle.inner),
              ],
      ),
      child: Stack(
        children: [
          AnimatedPositioned(
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOutCubic,
            left: selectedIndex * itemWidth,
            top: 0,
            bottom: 0,
            width: itemWidth,
            child: Container(
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF334155) : Colors.white,
                borderRadius: BorderRadius.circular(30),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(isDark ? 0.3 : 0.1),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
            ),
          ),
          Row(
            children: [
              _buildIcon(context, Icons.wb_sunny_rounded, 0, selectedIndex, ThemeMode.light),
              _buildIcon(context, Icons.nights_stay_rounded, 1, selectedIndex, ThemeMode.dark),
              _buildIcon(context, Icons.brightness_auto_rounded, 2, selectedIndex, ThemeMode.system),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildIcon(BuildContext context, IconData icon, int index, int selectedIndex, ThemeMode mode) {
    final isSelected = index == selectedIndex;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final activeColor = isDark ? Colors.white : Colors.black87;
    final inactiveColor = isDark ? Colors.white30 : Colors.black38;

    return Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => ThemeNotifier().setThemeMode(mode),
        child: Center(
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            child: Icon(
              icon,
              size: 26,
              color: isSelected ? activeColor : inactiveColor,
            ),
          ),
        ),
      ),
    );
  }
}
