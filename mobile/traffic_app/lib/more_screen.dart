import 'package:flutter/material.dart';

import 'admin_login_screen.dart';
import 'friends_screen.dart';
import 'metrics_screen.dart';
import 'theme_notifier.dart';
import 'common.dart';

/// Экран «Ещё» — доступ ко всем второстепенным разделам приложения.
class MoreScreen extends StatelessWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Ещё'),
        actions: [
          IconButton(
            icon: Icon(isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded),
            onPressed: () => ThemeNotifier().toggleTheme(),
            tooltip: isDark ? 'Светлая тема' : 'Тёмная тема',
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        children: [
          // ── Профиль / Информация ──
          _SectionHeader(title: 'Основное'),
          const SizedBox(height: 8),
          _MenuCard(
            children: [
              _MenuItem(
                icon: Icons.people_rounded,
                iconColor: const Color(0xFF8B5CF6),
                title: 'Друзья',
                subtitle: 'Список и карта друзей',
                onTap: () => Navigator.push(
                  context,
                  _buildPageRoute(const FriendsScreen()),
                ),
              ),
              _MenuDivider(),
              _MenuItem(
                icon: Icons.psychology_rounded,
                iconColor: const Color(0xFF0EA5E9),
                title: 'AI Аналитика',
                subtitle: 'Точность прогнозов моделей',
                onTap: () => Navigator.push(
                  context,
                  _buildPageRoute(const MetricsScreen()),
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),
          _SectionHeader(title: 'Управление'),
          const SizedBox(height: 8),
          _MenuCard(
            children: [
              _MenuItem(
                icon: Icons.admin_panel_settings_rounded,
                iconColor: const Color(0xFFF59E0B),
                title: 'Админ-панель',
                subtitle: 'Статистика и управление системой',
                onTap: () => Navigator.push(
                  context,
                  _buildPageRoute(const AdminLoginScreen()),
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),
          _SectionHeader(title: 'Настройки'),
          const SizedBox(height: 8),
          _MenuCard(
            children: [
              _MenuItem(
                icon: isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
                iconColor: const Color(0xFF6366F1),
                title: 'Тема оформления',
                subtitle: isDark ? 'Тёмная тема' : 'Светлая тема',
                trailing: Switch.adaptive(
                  value: isDark,
                  onChanged: (_) => ThemeNotifier().toggleTheme(),
                  activeColor: AppColors.primary,
                ),
                onTap: () => ThemeNotifier().toggleTheme(),
              ),
            ],
          ),

          const SizedBox(height: 32),

          // ── Версия приложения ──
          Center(
            child: Column(
              children: [
                Text(
                  'Traffic AI',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.5),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'v0.1.0 • Астана',
                  style: TextStyle(
                    fontSize: 13,
                    color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.35),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
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
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title.toUpperCase(),
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.2,
          color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.45),
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
