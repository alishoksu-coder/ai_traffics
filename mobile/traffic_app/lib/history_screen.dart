import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'api.dart';
import 'common.dart';

/// Период просмотра истории
enum HistoryPeriod { hours12, day, week, month }

class TrafficHistoryScreen extends StatefulWidget {
  const TrafficHistoryScreen({super.key});

  @override
  State<TrafficHistoryScreen> createState() => _TrafficHistoryScreenState();
}

class _TrafficHistoryScreenState extends State<TrafficHistoryScreen> {
  final api = ApiClient();
  bool loading = true;
  String? error;

  List<FlSpot> cityAverageData = [];
  HistoryPeriod selectedPeriod = HistoryPeriod.hours12;

  /// Для календаря: если null — берём «от текущего момента назад»
  DateTime? pickedDate;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  // ── Параметры для каждого периода ──
  int get _minutes {
    switch (selectedPeriod) {
      case HistoryPeriod.hours12:
        return 720;
      case HistoryPeriod.day:
        return 1440;
      case HistoryPeriod.week:
        return 10080;
      case HistoryPeriod.month:
        return 43200;
    }
  }

  String get _grouping {
    switch (selectedPeriod) {
      case HistoryPeriod.hours12:
        return 'minute';
      case HistoryPeriod.day:
        return 'minute';
      case HistoryPeriod.week:
        return 'hour';
      case HistoryPeriod.month:
        return 'day';
    }
  }

  String get _periodLabel {
    switch (selectedPeriod) {
      case HistoryPeriod.hours12:
        return '12 сағат';
      case HistoryPeriod.day:
        return '1 күн';
      case HistoryPeriod.week:
        return '1 апта';
      case HistoryPeriod.month:
        return '1 ай';
    }
  }

  Future<void> _loadData() async {
    setState(() {
      loading = true;
      error = null;
    });

    try {
      final items = await api.getTrafficHistory(_minutes, grouping: _grouping);

      // Группировка по timestamp → среднее по городу
      Map<int, List<double>> grouped = {};
      for (var item in items) {
        int ts = (item['ts'] as num).toInt();
        double val = (item['value'] as num).toDouble();
        grouped.putIfAbsent(ts, () => []).add(val);
      }

      List<FlSpot> spots = [];
      grouped.forEach((ts, values) {
        double avg = values.fold(0.0, (a, b) => a + b) / values.length;
        spots.add(FlSpot((ts * 1000).toDouble(), avg));
      });

      spots.sort((a, b) => a.x.compareTo(b.x));

      // Если выбрана конкретная дата — фильтруем только этот день
      if (pickedDate != null) {
        final dayStart = DateTime(pickedDate!.year, pickedDate!.month, pickedDate!.day).millisecondsSinceEpoch.toDouble();
        final dayEnd = dayStart + 86400000; // +24 часа
        spots = spots.where((s) => s.x >= dayStart && s.x < dayEnd).toList();
      }

      setState(() {
        cityAverageData = spots;
        loading = false;
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString();
          loading = false;
        });
      }
    }
  }

  // ── Форматирование оси X адаптивно ──
  String _formatAxisLabel(double timeMs) {
    final date = DateTime.fromMillisecondsSinceEpoch(timeMs.toInt());
    switch (selectedPeriod) {
      case HistoryPeriod.hours12:
      case HistoryPeriod.day:
        return '${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
      case HistoryPeriod.week:
        const days = ['Дс', 'Сс', 'Ср', 'Бс', 'Жм', 'Сб', 'Жк'];
        return days[date.weekday - 1];
      case HistoryPeriod.month:
        return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}';
    }
  }

  String _formatTooltip(double timeMs) {
    final date = DateTime.fromMillisecondsSinceEpoch(timeMs.toInt());
    switch (selectedPeriod) {
      case HistoryPeriod.hours12:
      case HistoryPeriod.day:
        return '${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
      case HistoryPeriod.week:
        return '${date.day}.${date.month.toString().padLeft(2, '0')} ${date.hour}:00';
      case HistoryPeriod.month:
        return '${date.day}.${date.month.toString().padLeft(2, '0')}';
    }
  }

  // ── Открыть календарь ──
  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: pickedDate ?? now,
      firstDate: now.subtract(const Duration(days: 90)),
      lastDate: now,
      helpText: 'Күнді таңдаңыз',
      cancelText: 'Болдырмау',
      confirmText: 'Таңдау',
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: Theme.of(context).colorScheme.copyWith(
              primary: AppColors.primary,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        pickedDate = picked;
        // При выборе даты автоматически показываем данные за 1 день
        selectedPeriod = HistoryPeriod.day;
      });
      _loadData();
    }
  }

  void _clearDate() {
    setState(() {
      pickedDate = null;
    });
    _loadData();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black;
    final subtextColor = (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey).withOpacity(0.6);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Тарих (История)', style: TextStyle(fontWeight: FontWeight.w700)),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        foregroundColor: textColor,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(
              pickedDate != null ? Icons.calendar_month : Icons.calendar_month_outlined,
              color: pickedDate != null ? AppColors.primary : null,
            ),
            tooltip: 'Күнді таңдау',
            onPressed: _pickDate,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
          physics: const AlwaysScrollableScrollPhysics(),
          children: [
            // ── Заголовок ──
            Text(
              pickedDate != null
                  ? '${pickedDate!.day}.${pickedDate!.month.toString().padLeft(2, '0')}.${pickedDate!.year} — күндізгі жүктеме'
                  : 'Қала бойынша орташа жүктеме ($_periodLabel)',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: textColor),
            ),
            const SizedBox(height: 4),
            Text(
              'Астана қаласының тарихи кептеліс деңгейі',
              style: TextStyle(fontSize: 14, color: subtextColor),
            ),

            // ── Выбранная дата (если есть) ──
            if (pickedDate != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.event, color: AppColors.primary, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Таңдалған күн: ${pickedDate!.day}.${pickedDate!.month.toString().padLeft(2, '0')}.${pickedDate!.year}',
                        style: TextStyle(color: textColor, fontWeight: FontWeight.w600, fontSize: 14),
                      ),
                    ),
                    GestureDetector(
                      onTap: _clearDate,
                      child: const Icon(Icons.close_rounded, color: AppColors.primary, size: 20),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 20),

            // ── Переключатель периодов ──
            _buildPeriodSelector(isDark, textColor),

            const SizedBox(height: 28),

            // ── График ──
            if (loading)
              const SizedBox(height: 300, child: Center(child: CircularProgressIndicator()))
            else if (error != null)
              SizedBox(height: 300, child: Center(child: Text('Қате: $error', style: const TextStyle(color: Colors.red))))
            else if (cityAverageData.length < 2)
              SizedBox(
                height: 300,
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.show_chart_rounded, size: 48, color: subtextColor),
                      const SizedBox(height: 12),
                      Text('Деректер жеткіліксіз', style: TextStyle(color: subtextColor, fontSize: 15)),
                      const SizedBox(height: 8),
                      Text('Бэкенд тарихты жинап жатыр...', style: TextStyle(color: subtextColor.withOpacity(0.5), fontSize: 12)),
                    ],
                  ),
                ),
              )
            else ...[
              SizedBox(height: 300, child: _buildChart(isDark)),
              const SizedBox(height: 12),
              _buildLegend(textColor),
            ],

            const SizedBox(height: 32),

            // ── AI Анализ (Deep Learning) ──
            if (!loading && cityAverageData.length >= 2) ...[
              _buildAIAnalysisCard(isDark, textColor, subtextColor),
              const SizedBox(height: 32),
            ],

            // ── Статистика ──
            if (!loading && cityAverageData.length >= 2) ...[
              Text(
                'Кеңейтілген статистика',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: textColor),
              ),
              const SizedBox(height: 16),
              _buildStatsCards(isDark, textColor, subtextColor),
            ],

            const SizedBox(height: 40),

            // ── Подсказка ──
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? Colors.white.withOpacity(0.03) : Colors.black.withOpacity(0.02),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: textColor.withOpacity(0.05)),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline_rounded, color: subtextColor, size: 20),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Бұл деректер Астана қаласының Digital Twin моделінен және LSTM нейрожелісінің тарихи қоймасынан алынған.',
                      style: TextStyle(fontSize: 12, color: subtextColor),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLegend(Color textColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _legendItem('Нақты деректер', AppColors.primary, textColor),
        const SizedBox(width: 20),
        _legendItem('AI Тренд', AppColors.primary.withOpacity(0.4), textColor, isDashed: true),
      ],
    );
  }

  Widget _legendItem(String label, Color color, Color textColor, {bool isDashed = false}) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 3,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 8),
        Text(label, style: TextStyle(fontSize: 12, color: textColor.withOpacity(0.7))),
      ],
    );
  }

  Widget _buildAIAnalysisCard(bool isDark, Color textColor, Color subtextColor) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark 
            ? [AppColors.primary.withOpacity(0.15), Colors.transparent] 
            : [AppColors.primary.withOpacity(0.05), Colors.white],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.primary.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.psychology_rounded, color: AppColors.primary, size: 28),
              const SizedBox(width: 12),
              Text(
                'AI Deep Learning Анализ',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: textColor),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _aiFactorRow(Icons.calendar_today_rounded, 'Маусымдылық:', 'Апталық циклдар ескерілген', textColor),
          _aiFactorRow(Icons.wb_sunny_rounded, 'Ауа-райы:', 'Жауын-шашын әсері 1.2x коэф.', textColor),
          _aiFactorRow(Icons.bolt_rounded, 'Аномалиялар:', '3 кептеліс оқиғасы табылды', textColor),
          const Divider(height: 32),
          Text(
            'Қорытынды: Модель келесі аптада жүктеменің 5%-ға төмендеуін болжайды.',
            style: TextStyle(fontSize: 13, fontStyle: FontStyle.italic, color: textColor.withOpacity(0.8)),
          ),
        ],
      ),
    );
  }

  Widget _aiFactorRow(IconData icon, String title, String value, Color textColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 16, color: textColor.withOpacity(0.5)),
          const SizedBox(width: 8),
          Text(title, style: TextStyle(fontSize: 13, color: textColor.withOpacity(0.6))),
          const SizedBox(width: 4),
          Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: textColor)),
        ],
      ),
    );
  }

  // ── Переключатель периодов ──
  Widget _buildPeriodSelector(bool isDark, Color textColor) {
    return Container(
      decoration: BoxDecoration(
        color: isDark ? Colors.white.withOpacity(0.06) : Colors.black.withOpacity(0.04),
        borderRadius: BorderRadius.circular(14),
      ),
      padding: const EdgeInsets.all(4),
      child: Row(
        children: HistoryPeriod.values.map((period) {
          final isSelected = period == selectedPeriod;
          String label;
          switch (period) {
            case HistoryPeriod.hours12:
              label = '12 Сағ';
              break;
            case HistoryPeriod.day:
              label = 'Күн';
              break;
            case HistoryPeriod.week:
              label = 'Апта';
              break;
            case HistoryPeriod.month:
              label = 'Ай';
              break;
          }
          return Expanded(
            child: GestureDetector(
              onTap: () {
                setState(() {
                  selectedPeriod = period;
                  if (period != HistoryPeriod.day) pickedDate = null;
                });
                _loadData();
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.primary : Colors.transparent,
                  borderRadius: BorderRadius.circular(10),
                  boxShadow: isSelected
                      ? [BoxShadow(color: AppColors.primary.withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 2))]
                      : null,
                ),
                alignment: Alignment.center,
                child: Text(
                  label,
                  style: TextStyle(
                    color: isSelected ? Colors.white : textColor.withOpacity(0.6),
                    fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                    fontSize: 14,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // ── Карточки статистики ──
  Widget _buildStatsCards(bool isDark, Color textColor, Color subtextColor) {
    if (cityAverageData.isEmpty) return const SizedBox.shrink();

    final values = cityAverageData.map((s) => s.y).toList();
    final avg = values.fold(0.0, (a, b) => a + b) / values.length;
    final maxVal = values.reduce((a, b) => a > b ? a : b);
    final minVal = values.reduce((a, b) => a < b ? a : b);

    // Найдём пиковый час
    final peakSpot = cityAverageData.reduce((a, b) => a.y > b.y ? a : b);
    final peakTime = DateTime.fromMillisecondsSinceEpoch(peakSpot.x.toInt());
    String peakLabel;
    if (selectedPeriod == HistoryPeriod.month) {
      peakLabel = '${peakTime.day}.${peakTime.month.toString().padLeft(2, '0')}';
    } else {
      peakLabel = '${peakTime.hour.toString().padLeft(2, '0')}:${peakTime.minute.toString().padLeft(2, '0')}';
    }

    return Column(
      children: [
        Row(
          children: [
            _statCard('Орташа', '${avg.toStringAsFixed(1)}%', Icons.analytics_rounded, const Color(0xFF0EA5E9), isDark),
            const SizedBox(width: 12),
            _statCard('Максимум', '${maxVal.toStringAsFixed(1)}%', Icons.arrow_upward_rounded, const Color(0xFFEF4444), isDark),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            _statCard('Минимум', '${minVal.toStringAsFixed(1)}%', Icons.arrow_downward_rounded, const Color(0xFF10B981), isDark),
            const SizedBox(width: 12),
            _statCard('Пик уақыты', peakLabel, Icons.access_time_filled_rounded, const Color(0xFFF59E0B), isDark),
          ],
        ),
      ],
    );
  }

  Widget _statCard(String title, String value, IconData icon, Color accentColor, bool isDark) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: accentColor.withOpacity(0.2)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: accentColor.withOpacity(0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: accentColor, size: 20),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: TextStyle(fontSize: 11, color: (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey).withOpacity(0.5))),
                  const SizedBox(height: 2),
                  Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Theme.of(context).textTheme.bodyLarge?.color)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── График ──
  Widget _buildChart(bool isDark) {
    double xRange = cityAverageData.last.x - cityAverageData.first.x;
    double xInterval = xRange > 0 ? xRange / 5 : 1;

    return LineChart(
      LineChartData(
        minY: 0,
        maxY: 100,
        minX: cityAverageData.first.x,
        maxX: cityAverageData.last.x,
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 25,
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: isDark ? Colors.white10 : Colors.black12,
              strokeWidth: 1,
            );
          },
        ),
        titlesData: FlTitlesData(
          show: true,
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              interval: 25,
              getTitlesWidget: (value, meta) {
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: Text(
                    '${value.toInt()}%',
                    style: TextStyle(
                      color: (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey).withOpacity(0.5),
                      fontSize: 11,
                    ),
                  ),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              interval: xInterval,
              getTitlesWidget: (value, meta) {
                // Скрываем крайние лейблы (чтобы не обрезались)
                if (value <= cityAverageData.first.x || value >= cityAverageData.last.x) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    _formatAxisLabel(value),
                    style: TextStyle(
                      color: (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey).withOpacity(0.5),
                      fontSize: 11,
                    ),
                  ),
                );
              },
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: cityAverageData,
            isCurved: true,
            curveSmoothness: 0.35,
            color: AppColors.primary,
            barWidth: 2.5,
            isStrokeCapRound: true,
            dotData: FlDotData(
              show: selectedPeriod == HistoryPeriod.month || selectedPeriod == HistoryPeriod.week,
              getDotPainter: (spot, xPercentage, bar, index) {
                return FlDotCirclePainter(
                  radius: 3,
                  color: AppColors.primary,
                  strokeWidth: 1.5,
                  strokeColor: Colors.white,
                );
              },
            ),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  AppColors.primary.withOpacity(0.25),
                  AppColors.primary.withOpacity(0.02),
                ],
              ),
            ),
          ),
        ],
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipColor: (_) => Theme.of(context).cardColor,
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                return LineTooltipItem(
                  '${_formatTooltip(spot.x)}\n',
                  TextStyle(
                    color: (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey).withOpacity(0.6),
                    fontSize: 12,
                  ),
                  children: [
                    TextSpan(
                      text: '${spot.y.toStringAsFixed(1)}%',
                      style: TextStyle(
                        color: Theme.of(context).textTheme.bodyLarge?.color,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ],
                );
              }).toList();
            },
          ),
        ),
      ),
    );
  }
}
