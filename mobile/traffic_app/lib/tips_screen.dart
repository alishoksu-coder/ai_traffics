import 'package:flutter/material.dart';

import 'api.dart';
import 'models.dart';
import 'common.dart';
import 'admin_login_screen.dart';
import 'metrics_screen.dart';

class TipsScreen extends StatefulWidget {
  const TipsScreen({super.key});

  @override
  State<TipsScreen> createState() => _TipsScreenState();
}

class _TipsScreenState extends State<TipsScreen> {
  final api = ApiClient();

  int horizon = 30;
  bool loading = true;
  String? error;
  List<RoadSegment> segments = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final items = await api.getRoadSegments(horizon);
      final clean = items.where((s) => s.points.length >= 2).toList();
      clean.sort((a, b) => (b.value ?? -1).compareTo(a.value ?? -1));
      setState(() {
        segments = clean;
        loading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  String _getTrafficLevel(double? value) {
    if (value == null) return 'Неизвестно';
    if (value <= 30) return 'Свободно';
    if (value <= 60) return 'Загружено';
    return 'Пробка';
  }

  String _getRecommendation(double? value) {
    if (value == null) return 'Данных недостаточно';
    if (value <= 30) return 'Маршрут свободен';
    if (value <= 60) return 'Рекомендуется объехать';
    return 'Серьёзная пробка — выберите альтернативный маршрут';
  }

  IconData _getTrafficIcon(double? value) {
    if (value == null) return Icons.help_outline;
    if (value <= 30) return Icons.check_circle;
    if (value <= 60) return Icons.warning;
    return Icons.error;
  }

  @override
  Widget build(BuildContext context) {
    final top = segments.take(10).toList();
    final heavy = top.where((s) => (s.value ?? 0) > 60).toList();
    final moderate = top.where((s) {
      final v = s.value ?? 0;
      return v > 30 && v <= 60;
    }).toList();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: whiteAppBar(
        'AI Рекомендации',
        actions: [
          if (!loading)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _load,
              tooltip: 'Обновить',
            ),
          if (loading)
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
        ],
      ),
      body: Column(
        children: [
          Container(
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: AppColors.cardBackground,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.06),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              children: [
                const Icon(Icons.psychology, size: 20, color: AppColors.primary),
                const SizedBox(width: 12),
                const Text(
                  'Прогноз:',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppColors.background,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: DropdownButton<int>(
                      value: horizon,
                      isExpanded: true,
                      underline: const SizedBox(),
                      items: const [
                        DropdownMenuItem(value: 0, child: Text('Сейчас')),
                        DropdownMenuItem(value: 30, child: Text('+30 мин')),
                        DropdownMenuItem(value: 60, child: Text('+60 мин')),
                      ],
                      onChanged: (v) {
                        if (v == null) return;
                        setState(() => horizon = v);
                        _load();
                      },
                    ),
                  ),
                ),
              ],
            ),
          ),
          if (error != null)
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, color: Colors.red, size: 20),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      error!,
                      style: const TextStyle(color: Colors.red, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          Expanded(
            child: loading
                ? const Center(
                    child: CircularProgressIndicator(color: AppColors.primary),
                  )
                : top.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.map_outlined, size: 64, color: AppColors.textSecondary),
                            const SizedBox(height: 16),
                            Text(
                              'Нет данных по сегментам',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                          ],
                        ),
                      )
                    : ListView(
                        padding: const EdgeInsets.all(16),
                        children: [
                          if (heavy.isNotEmpty) ...[
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.red.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: Colors.red.withOpacity(0.3)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.error, color: Colors.red, size: 24),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          'Критические пробки',
                                          style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.w700,
                                            color: Colors.red,
                                          ),
                                        ),
                                        Text(
                                          'Найдено ${heavy.length} сегментов с высокой загрузкой',
                                          style: const TextStyle(
                                            fontSize: 12,
                                            color: AppColors.textSecondary,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),
                          ],
                          ...top.map((s) {
                            final value = s.value ?? 0;
                            final isHeavy = value > 60;
                            final isModerate = value > 30 && value <= 60;
                            
                            return Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AppColors.cardBackground,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: isHeavy
                                      ? Colors.red.withOpacity(0.5)
                                      : isModerate
                                          ? Colors.orange.withOpacity(0.3)
                                          : AppColors.divider,
                                  width: isHeavy ? 2 : 1,
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withOpacity(0.04),
                                    blurRadius: 8,
                                    offset: const Offset(0, 2),
                                  ),
                                ],
                              ),
                              child: Row(
                                children: [
                                  Container(
                                    width: 48,
                                    height: 48,
                                    decoration: BoxDecoration(
                                      color: colorByValue(s.value).withOpacity(0.15),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: Icon(
                                      _getTrafficIcon(s.value),
                                      color: colorByValue(s.value),
                                      size: 24,
                                    ),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          s.name.isEmpty ? 'Сегмент ${s.id}' : s.name,
                                          style: const TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.w600,
                                            color: AppColors.textPrimary,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          _getRecommendation(s.value),
                                          style: const TextStyle(
                                            fontSize: 13,
                                            color: AppColors.textSecondary,
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        Row(
                                          children: [
                                            Container(
                                              padding: const EdgeInsets.symmetric(
                                                horizontal: 8,
                                                vertical: 4,
                                              ),
                                              decoration: BoxDecoration(
                                                color: colorByValue(s.value).withOpacity(0.15),
                                                borderRadius: BorderRadius.circular(6),
                                              ),
                                              child: Text(
                                                _getTrafficLevel(s.value),
                                                style: TextStyle(
                                                  fontSize: 11,
                                                  fontWeight: FontWeight.w600,
                                                  color: colorByValue(s.value),
                                                ),
                                              ),
                                            ),
                                            const SizedBox(width: 8),
                                            Text(
                                              'Загрузка: ${s.value?.toStringAsFixed(0) ?? '—'}%',
                                              style: const TextStyle(
                                                fontSize: 11,
                                                color: AppColors.textSecondary,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }),
                          const SizedBox(height: 24),
                          ListTile(
                            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            leading: const CircleAvatar(child: Icon(Icons.psychology)),
                            title: const Text('AI Аналитика', style: TextStyle(fontWeight: FontWeight.w600)),
                            subtitle: const Text('Точность прогнозов'),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const MetricsScreen())),
                          ),
                          ListTile(
                            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            leading: const CircleAvatar(child: Icon(Icons.admin_panel_settings)),
                            title: const Text('Админ-панель', style: TextStyle(fontWeight: FontWeight.w600)),
                            subtitle: const Text('Вход по логину и паролю'),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminLoginScreen())),
                          ),
                        ],
                      ),
          ),
        ],
      ),
    );
  }
}
