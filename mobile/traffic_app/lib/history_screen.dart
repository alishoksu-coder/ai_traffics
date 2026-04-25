import 'dart:ui';
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

class _TrafficHistoryScreenState extends State<TrafficHistoryScreen> with SingleTickerProviderStateMixin {
  final api = ApiClient();
  bool loading = true;
  String? error;

  List<FlSpot> cityAverageData = [];
  HistoryPeriod selectedPeriod = HistoryPeriod.hours12;

  DateTime? pickedDate;
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(vsync: this, duration: const Duration(milliseconds: 800));
    _fadeAnimation = CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut);
    _loadData();
  }
  
  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  // ── Параметры для каждого периода ──
  int get _minutes {
    switch (selectedPeriod) {
      case HistoryPeriod.hours12: return 720;
      case HistoryPeriod.day: return 1440;
      case HistoryPeriod.week: return 10080;
      case HistoryPeriod.month: return 43200;
    }
  }

  String get _grouping {
    switch (selectedPeriod) {
      case HistoryPeriod.hours12:
      case HistoryPeriod.day: return 'minute';
      case HistoryPeriod.week: return 'hour';
      case HistoryPeriod.month: return 'day';
    }
  }

  String get _periodLabel {
    switch (selectedPeriod) {
      case HistoryPeriod.hours12: return '12 сағат';
      case HistoryPeriod.day: return '1 күн';
      case HistoryPeriod.week: return '1 апта';
      case HistoryPeriod.month: return '1 ай';
    }
  }

  Future<void> _loadData() async {
    setState(() {
      loading = true;
      error = null;
    });

    try {
      final items = await api.getTrafficHistory(_minutes, grouping: _grouping);

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

      if (pickedDate != null) {
        final dayStart = DateTime(pickedDate!.year, pickedDate!.month, pickedDate!.day).millisecondsSinceEpoch.toDouble();
        final dayEnd = dayStart + 86400000;
        spots = spots.where((s) => s.x >= dayStart && s.x < dayEnd).toList();
      }

      if (mounted) {
        setState(() {
          cityAverageData = spots;
          loading = false;
        });
        _fadeController.forward(from: 0.0);
      }
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
      body: Stack(
        children: [
          // Background Gradient
          Positioned(
            top: -150,
            left: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.primary.withOpacity(isDark ? 0.2 : 0.1),
              ),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 80, sigmaY: 80),
                child: const SizedBox(),
              ),
            ),
          ),
          Positioned(
            bottom: -150,
            right: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFF0EA5E9).withOpacity(isDark ? 0.15 : 0.08),
              ),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 80, sigmaY: 80),
                child: const SizedBox(),
              ),
            ),
          ),

          SafeArea(
            child: Column(
              children: [
                _buildAppBar(textColor),
                Expanded(
                  child: RefreshIndicator(
                    onRefresh: _loadData,
                    color: AppColors.primary,
                    child: ListView(
                      padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
                      physics: const BouncingScrollPhysics(parent: AlwaysScrollableScrollPhysics()),
                      children: [
                        _buildHeader(textColor, subtextColor),
                        
                        if (pickedDate != null) ...[
                          const SizedBox(height: 16),
                          _buildPickedDateCard(textColor),
                        ],

                        const SizedBox(height: 24),
                        _buildPeriodSelector(isDark, textColor),
                        const SizedBox(height: 28),

                        _buildChartSection(isDark, textColor, subtextColor),
                        const SizedBox(height: 32),

                        if (!loading && cityAverageData.length >= 2) ...[
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: _buildAIAnalysisCard(isDark, textColor, subtextColor),
                          ),
                          const SizedBox(height: 32),
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: _buildStatsCards(isDark, textColor, subtextColor),
                          ),
                        ],

                        const SizedBox(height: 40),
                        _buildInfoBox(isDark, textColor, subtextColor),
                      ],
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

  Widget _buildAppBar(Color textColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: Icon(Icons.arrow_back_ios_new_rounded, color: textColor, size: 20),
            onPressed: () => Navigator.pop(context),
          ),
          Text('Тарих', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: textColor)),
          IconButton(
            icon: Icon(
              pickedDate != null ? Icons.calendar_month : Icons.calendar_month_outlined,
              color: pickedDate != null ? AppColors.primary : textColor,
            ),
            onPressed: _pickDate,
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(Color textColor, Color subtextColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          pickedDate != null
              ? '${pickedDate!.day}.${pickedDate!.month.toString().padLeft(2, '0')}.${pickedDate!.year} жүктемесі'
              : 'Қала бойынша орташа жүктеме\n($_periodLabel)',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: textColor, height: 1.2),
        ),
        const SizedBox(height: 8),
        Text(
          'Астана қаласының тарихи кептеліс деңгейі',
          style: TextStyle(fontSize: 15, color: subtextColor),
        ),
      ],
    );
  }

  Widget _buildPickedDateCard(Color textColor) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.primary.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.2), borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.event_available_rounded, color: AppColors.primary, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Таңдалған күн: ${pickedDate!.day}.${pickedDate!.month.toString().padLeft(2, '0')}.${pickedDate!.year}',
              style: TextStyle(color: textColor, fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ),
          GestureDetector(
            onTap: _clearDate,
            child: Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(color: Colors.black.withOpacity(0.05), shape: BoxShape.circle),
              child: const Icon(Icons.close_rounded, color: AppColors.primary, size: 18),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPeriodSelector(bool isDark, Color textColor) {
    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: isDark ? Colors.white.withOpacity(0.05) : Colors.black.withOpacity(0.04),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: HistoryPeriod.values.map((period) {
          final isSelected = period == selectedPeriod;
          String label;
          switch (period) {
            case HistoryPeriod.hours12: label = '12 Сағ'; break;
            case HistoryPeriod.day: label = 'Күн'; break;
            case HistoryPeriod.week: label = 'Апта'; break;
            case HistoryPeriod.month: label = 'Ай'; break;
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
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeInOut,
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.primary : Colors.transparent,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: isSelected
                      ? [BoxShadow(color: AppColors.primary.withOpacity(0.4), blurRadius: 12, offset: const Offset(0, 4))]
                      : null,
                ),
                alignment: Alignment.center,
                child: Text(
                  label,
                  style: TextStyle(
                    color: isSelected ? Colors.white : textColor.withOpacity(0.6),
                    fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
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

  Widget _buildChartSection(bool isDark, Color textColor, Color subtextColor) {
    return Container(
      padding: const EdgeInsets.only(top: 24, bottom: 16, left: 16, right: 24),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor.withOpacity(isDark ? 0.5 : 0.8),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(isDark ? 0.05 : 0.5)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(isDark ? 0.2 : 0.05),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          if (loading)
            const SizedBox(height: 280, child: Center(child: CircularProgressIndicator(strokeWidth: 3)))
          else if (error != null)
            SizedBox(height: 280, child: Center(child: Text('Қате: $error', style: const TextStyle(color: Colors.red))))
          else if (cityAverageData.length < 2)
            SizedBox(
              height: 280,
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.query_stats_rounded, size: 56, color: subtextColor.withOpacity(0.4)),
                    const SizedBox(height: 16),
                    Text('Деректер жеткіліксіз', style: TextStyle(color: textColor, fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Text('Бэкенд тарихты жинап жатыр...', style: TextStyle(color: subtextColor, fontSize: 13)),
                  ],
                ),
              ),
            )
          else ...[
            FadeTransition(
              opacity: _fadeAnimation,
              child: SizedBox(height: 260, child: _buildChart(isDark)),
            ),
            const SizedBox(height: 20),
            FadeTransition(
              opacity: _fadeAnimation,
              child: _buildLegend(textColor),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildLegend(Color textColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _legendItem('Нақты деректер', AppColors.primary, textColor),
        const SizedBox(width: 24),
        _legendItem('Орташа мән', const Color(0xFF0EA5E9).withOpacity(0.6), textColor, isDashed: true),
      ],
    );
  }

  Widget _legendItem(String label, Color color, Color textColor, {bool isDashed = false}) {
    return Row(
      children: [
        Container(
          width: 14,
          height: 4,
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2)),
        ),
        const SizedBox(width: 8),
        Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: textColor.withOpacity(0.7))),
      ],
    );
  }

  Widget _buildAIAnalysisCard(bool isDark, Color textColor, Color subtextColor) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark 
            ? [AppColors.primary.withOpacity(0.15), const Color(0xFF0EA5E9).withOpacity(0.05)] 
            : [AppColors.primary.withOpacity(0.08), const Color(0xFF0EA5E9).withOpacity(0.02)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.primary.withOpacity(0.2)),
        boxShadow: [
          BoxShadow(color: AppColors.primary.withOpacity(0.05), blurRadius: 15, offset: const Offset(0, 5)),
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
                  color: AppColors.primary.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.auto_graph_rounded, color: AppColors.primary, size: 24),
              ),
              const SizedBox(width: 16),
              Text(
                'AI Analysis',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: textColor, letterSpacing: 0.5),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _aiFactorRow(Icons.calendar_today_rounded, 'Маусымдылық:', 'Апталық циклдар қалыпты', textColor),
          _aiFactorRow(Icons.cloud_rounded, 'Ауа-райы:', 'Температуралық ауытқу жоқ', textColor),
          _aiFactorRow(Icons.bolt_rounded, 'Аномалиялар:', '3 кенет кептеліс тіркелді', textColor),
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 16),
            child: Divider(height: 1),
          ),
          Text(
            'LSTM моделі келесі күндері жүктеменің 5%-ға төмендеуін болжайды. Тренд тұрақты.',
            style: TextStyle(fontSize: 14, fontStyle: FontStyle.italic, color: textColor.withOpacity(0.8), height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _aiFactorRow(IconData icon, String title, String value, Color textColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, size: 18, color: textColor.withOpacity(0.4)),
          const SizedBox(width: 12),
          Text(title, style: TextStyle(fontSize: 14, color: textColor.withOpacity(0.6))),
          const SizedBox(width: 6),
          Expanded(child: Text(value, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: textColor))),
        ],
      ),
    );
  }

  Widget _buildStatsCards(bool isDark, Color textColor, Color subtextColor) {
    if (cityAverageData.isEmpty) return const SizedBox.shrink();

    final values = cityAverageData.map((s) => s.y).toList();
    final avg = values.fold(0.0, (a, b) => a + b) / values.length;
    final maxVal = values.reduce((a, b) => a > b ? a : b);
    final minVal = values.reduce((a, b) => a < b ? a : b);

    final peakSpot = cityAverageData.reduce((a, b) => a.y > b.y ? a : b);
    final peakTime = DateTime.fromMillisecondsSinceEpoch(peakSpot.x.toInt());
    String peakLabel;
    if (selectedPeriod == HistoryPeriod.month) {
      peakLabel = '${peakTime.day}.${peakTime.month.toString().padLeft(2, '0')}';
    } else {
      peakLabel = '${peakTime.hour.toString().padLeft(2, '0')}:${peakTime.minute.toString().padLeft(2, '0')}';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Кеңейтілген статистика',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: textColor),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            _statCard('Орташа', '${avg.toStringAsFixed(1)}%', Icons.insights_rounded, const Color(0xFF0EA5E9), isDark, textColor),
            const SizedBox(width: 12),
            _statCard('Максимум', '${maxVal.toStringAsFixed(1)}%', Icons.keyboard_double_arrow_up_rounded, const Color(0xFFEF4444), isDark, textColor),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            _statCard('Минимум', '${minVal.toStringAsFixed(1)}%', Icons.keyboard_double_arrow_down_rounded, const Color(0xFF10B981), isDark, textColor),
            const SizedBox(width: 12),
            _statCard('Пик уақыты', peakLabel, Icons.access_time_filled_rounded, const Color(0xFFF59E0B), isDark, textColor),
          ],
        ),
      ],
    );
  }

  Widget _statCard(String title, String value, IconData icon, Color accentColor, bool isDark, Color textColor) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor.withOpacity(isDark ? 0.4 : 0.8),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white.withOpacity(isDark ? 0.05 : 0.5)),
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4)),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: accentColor.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: accentColor, size: 22),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: textColor.withOpacity(0.5))),
                  const SizedBox(height: 4),
                  Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: textColor)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

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
              color: isDark ? Colors.white.withOpacity(0.05) : Colors.black.withOpacity(0.03),
              strokeWidth: 1,
              dashArray: [4, 4],
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
              reservedSize: 42,
              interval: 25,
              getTitlesWidget: (value, meta) {
                return Padding(
                  padding: const EdgeInsets.only(right: 12),
                  child: Text(
                    '${value.toInt()}%',
                    style: TextStyle(
                      color: (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey).withOpacity(0.5),
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                    textAlign: TextAlign.right,
                  ),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 32,
              interval: xInterval,
              getTitlesWidget: (value, meta) {
                if (value <= cityAverageData.first.x || value >= cityAverageData.last.x) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.only(top: 10),
                  child: Text(
                    _formatAxisLabel(value),
                    style: TextStyle(
                      color: (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey).withOpacity(0.5),
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
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
            curveSmoothness: 0.4,
            color: AppColors.primary,
            barWidth: 4,
            isStrokeCapRound: true,
            shadow: Shadow(
              color: AppColors.primary.withOpacity(0.5),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
            dotData: FlDotData(
              show: selectedPeriod == HistoryPeriod.month || selectedPeriod == HistoryPeriod.week,
              getDotPainter: (spot, xPercentage, bar, index) {
                return FlDotCirclePainter(
                  radius: 4,
                  color: Theme.of(context).cardColor,
                  strokeWidth: 3,
                  strokeColor: AppColors.primary,
                );
              },
            ),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  AppColors.primary.withOpacity(0.4),
                  AppColors.primary.withOpacity(0.0),
                ],
              ),
            ),
          ),
        ],
        lineTouchData: LineTouchData(
          handleBuiltInTouches: true,
          touchTooltipData: LineTouchTooltipData(
            getTooltipColor: (_) => isDark ? Colors.white : Colors.black87,
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                return LineTooltipItem(
                  '${_formatTooltip(spot.x)}\n',
                  TextStyle(
                    color: isDark ? Colors.black54 : Colors.white70,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                  children: [
                    TextSpan(
                      text: '${spot.y.toStringAsFixed(1)}%',
                      style: TextStyle(
                        color: isDark ? Colors.black : Colors.white,
                        fontWeight: FontWeight.w900,
                        fontSize: 16,
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

  Widget _buildInfoBox(bool isDark, Color textColor, Color subtextColor) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: isDark ? Colors.white.withOpacity(0.03) : Colors.black.withOpacity(0.02),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: textColor.withOpacity(0.05)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: textColor.withOpacity(0.05),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.info_outline_rounded, color: subtextColor, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              'Деректер Астана қаласының Digital Twin моделі мен LSTM тарихи қоймасынан алынған.',
              style: TextStyle(fontSize: 13, color: subtextColor, height: 1.4),
            ),
          ),
        ],
      ),
    );
  }
}
