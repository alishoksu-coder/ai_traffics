import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'package:traffic_app/config.dart';
import 'package:traffic_app/common.dart';

class MetricsScreen extends StatefulWidget {
  const MetricsScreen({super.key});

  @override
  State<MetricsScreen> createState() => _MetricsScreenState();
}

class _MetricsScreenState extends State<MetricsScreen> {
  bool loading = true;
  String? error;

  Map<String, dynamic>? m30;
  Map<String, dynamic>? m60;

  Future<Map<String, dynamic>> _getMetrics(int horizon, int minutes) async {
    final uri = Uri.parse(
        '$kApiBaseUrl/traffic/metrics?horizon=$horizon&minutes=$minutes');
    final r = await http.get(uri).timeout(const Duration(seconds: 10));
    if (r.statusCode != 200) throw Exception('HTTP ${r.statusCode}: ${r.body}');
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

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
      final a = await _getMetrics(30, 240);
      final b = await _getMetrics(60, 240);
      setState(() {
        m30 = a;
        m60 = b;
        loading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  String _getBestModel(Map<String, dynamic>? m) {
    if (m == null) return '—';
    final naive = m['naive'] as Map<String, dynamic>?;
    final ma = m['moving_avg'] as Map<String, dynamic>?;
    final trend = m['trend_lr'] as Map<String, dynamic>?;
    
    double? bestMae;
    String? bestName;
    
    final models = [
      {'name': 'Naive', 'data': naive},
      {'name': 'Moving Avg', 'data': ma},
      {'name': 'Trend LR', 'data': trend},
    ];
    
    for (final model in models) {
      final data = model['data'] as Map<String, dynamic>?;
      final mae = data?['mae'] as num?;
      if (mae != null && (bestMae == null || mae.toDouble() < bestMae)) {
        bestMae = mae.toDouble();
        bestName = model['name'] as String;
      }
    }
    
    return bestName ?? '—';
  }

  Widget _card(String title, Map<String, dynamic>? m, IconData icon) {
    if (m == null) return const SizedBox.shrink();

    Widget row(String name, String description, Map<String, dynamic> mm, Color color) {
      final maeRaw = mm['mae'];
      final rmseRaw = mm['rmse'];
      final mae = maeRaw != null ? (maeRaw as num).toDouble() : null;
      final rmse = rmseRaw != null ? (rmseRaw as num).toDouble() : null;
      final n = mm['n'] as int? ?? 0;
      final isBest = _getBestModel(m) == name;
      
      return Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.cardBackground,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isBest ? AppColors.primary : AppColors.divider,
            width: isBest ? 2 : 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: color, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            name,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          if (isBest) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppColors.primary,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Text(
                                'Лучшая',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      if (description.isNotEmpty)
                        Text(
                          description,
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
            const SizedBox(height: 12),
            if (mae != null && rmse != null)
              Row(
                children: [
                  Expanded(
                    child: _metricChip('MAE', mae.toStringAsFixed(2), Icons.trending_down),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _metricChip('RMSE', rmse.toStringAsFixed(2), Icons.analytics),
                  ),
                  if (n > 0) ...[
                    const SizedBox(width: 8),
                    Expanded(
                      child: _metricChip('Образцов', n.toString(), Icons.data_usage),
                    ),
                  ],
                ],
              )
            else
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: Text(
                  'Недостаточно данных для оценки',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 12,
                  ),
                ),
              ),
          ],
        ),
      );
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.psychology, color: AppColors.primary, size: 24),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    Text(
                      'AI анализ точности прогнозов',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.history, size: 16, color: AppColors.textSecondary),
                const SizedBox(width: 8),
                Text(
                  'Данные за ${m['minutes_used'] ?? '—'} минут',
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          row('Naive', 'Последнее значение', m['naive'] as Map<String, dynamic>? ?? {}, const Color(0xFF8E8E93)),
          row('Moving Avg', 'Скользящее среднее (k=5)', m['moving_avg'] as Map<String, dynamic>? ?? {}, const Color(0xFF34C759)),
          row('Trend LR', 'Линейная регрессия', m['trend_lr'] as Map<String, dynamic>? ?? {}, AppColors.primary),
        ],
      ),
    );
  }

  Widget _metricChip(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppColors.textSecondary),
          const SizedBox(width: 6),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 10,
                  color: AppColors.textSecondary,
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: whiteAppBar(
        'AI Аналитика',
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
      body: loading
          ? const Center(
              child: CircularProgressIndicator(color: AppColors.primary),
            )
          : (error != null)
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.error_outline,
                          size: 64,
                          color: Colors.red,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Ошибка загрузки',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          error!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: 24),
                        ElevatedButton.icon(
                          onPressed: _load,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Повторить'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(
                              horizontal: 24,
                              vertical: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    _card('Прогноз на +30 мин', m30, Icons.access_time),
                    _card('Прогноз на +60 мин', m60, Icons.schedule),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: AppColors.primary.withOpacity(0.3),
                        ),
                      ),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.info_outline,
                            color: AppColors.primary,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'AI сравнивает точность разных методов прогнозирования. Лучшая модель выделена синим.',
                              style: TextStyle(
                                fontSize: 12,
                                color: AppColors.primary,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
    );
  }
}
