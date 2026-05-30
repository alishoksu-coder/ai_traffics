import 'package:flutter/material.dart';

import '../../ui/screens/admin_login_screen.dart';
import '../../ui/screens/friends_screen.dart';
import '../../ui/screens/metrics_screen.dart';
import '../../ui/screens/history_screen.dart';
import '../../core/theme_notifier.dart';
import '../../ui/screens/auth_screen.dart';
import '../../ui/screens/security_settings_screen.dart';

/// Экран «Ещё» — доступ ко всем второстепенным разделам приложения.
class MoreScreen extends StatelessWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    const purpleColor = Color(0xFF4C45E5);

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
                      'Тағы',
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
                        color: Colors.white.withValues(alpha: 0.8),
                      ),
                    ),
                  ],
                ),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: IconButton(
                    icon: Icon(isDark ? Icons.wb_sunny_rounded : Icons.nights_stay_rounded, color: Colors.white),
                    onPressed: () => ThemeNotifier().toggleTheme(),
                    tooltip: isDark ? 'Жарық тақырып' : 'Қараңғы тақырып',
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
                    const _SectionHeader(title: 'Негізгі'),
                    const SizedBox(height: 12),
                  _MenuCard(
                    children: [
                      _MenuItem(
                        icon: Icons.people_rounded,
                        iconColor: const Color(0xFF8B5CF6),
                        title: 'Достар',
                        subtitle: 'Достар тізімі және карта',
                        onTap: () => Navigator.push(context, _buildPageRoute(const FriendsScreen())),
                      ),
                      _MenuDivider(),
                      _MenuItem(
                        icon: Icons.psychology_rounded,
                        iconColor: const Color(0xFF0EA5E9),
                        title: 'AI Аналитикасы',
                        subtitle: 'Модельдер болжамдарының дәлдігі',
                        onTap: () => Navigator.push(context, _buildPageRoute(const MetricsScreen())),
                      ),
                      _MenuDivider(),
                      _MenuItem(
                        icon: Icons.history_rounded,
                        iconColor: const Color(0xFFF43F5E),
                        title: 'Трафик тарихы',
                        subtitle: '12 сағат, күн, апта және ай',
                        onTap: () => Navigator.push(context, _buildPageRoute(const TrafficHistoryScreen())),
                      ),
                    ],
                  ),
        
                  const SizedBox(height: 28),
                  // ── Управление ──
                  const _SectionHeader(title: 'Басқару'),
                  const SizedBox(height: 12),
                  _MenuCard(
                    children: [
                      _MenuItem(
                        icon: Icons.admin_panel_settings_rounded,
                        iconColor: const Color(0xFFF59E0B),
                        title: 'Админ-панелі',
                        subtitle: 'Настройки системы',
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
                  const _SectionHeader(title: 'Аккаунт'),
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
                  // ── Настройки ──
                  const _SectionHeader(title: 'Сыртқы түрі'),
                  const SizedBox(height: 12),
                  _MenuCard(
                    children: [
                      _MenuItem(
                        icon: Icons.palette_rounded,
                        iconColor: const Color(0xFFEC4899),
                        title: 'Бездеу тақырыбы',
                        subtitle: isDark ? 'Қараңғы тақырып қосылды' : 'Жарық тақырып қосылды',
                        trailing: Switch.adaptive(
                          value: isDark,
                          onChanged: (_) => ThemeNotifier().toggleTheme(),
                          activeColor: purpleColor,
                        ),
                        onTap: () => ThemeNotifier().toggleTheme(),
                      ),
                    ],
                  ),
        
                  const SizedBox(height: 48),
                  // ── Версия ──
                  Center(
                    child: Column(
                      children: [
                        Text(
                          'Traffic AI',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.4)),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'v0.1.0 • Astana',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.3)),
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
          color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.4),
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
          color: isDark ? Colors.white.withValues(alpha: 0.08) : Colors.black.withValues(alpha: 0.06),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: isDark ? 0.2 : 0.05),
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
      color: Theme.of(context).dividerColor.withValues(alpha: 0.5),
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
                  color: iconColor.withValues(alpha: 0.12),
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
                        color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.55),
                      ),
                    ),
                  ],
                ),
              ),
              trailing ??
                  Icon(
                    Icons.chevron_right_rounded,
                    color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.3),
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
