import 'package:flutter/material.dart';

import 'api.dart';
import 'models.dart';
import 'package:traffic_app/common.dart';
import 'segment_map_page.dart';

class DriveScreen extends StatefulWidget {
  const DriveScreen({super.key});

  @override
  State<DriveScreen> createState() => _DriveScreenState();
}

class _DriveScreenState extends State<DriveScreen> {
  final api = ApiClient();

  int horizon = 0;
  bool loading = true;
  String? error;
  List<RoadSegment> segments = [];
  String query = '';

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

  List<RoadSegment> get filtered {
    final q = query.trim().toLowerCase();
    if (q.isEmpty) return segments;
    return segments.where((s) {
      final street = _streetName(s);
      return street.toLowerCase().contains(q) ||
          s.name.toLowerCase().contains(q) ||
          s.locationName.toLowerCase().contains(q) ||
          s.id.toString().contains(q) ||
          s.locationId.toString().contains(q);
    }).toList();
  }

  /// Название улицы/участка для отображения.
  String _streetName(RoadSegment s) {
    if (s.name.trim().isNotEmpty) return s.name.trim();
    if (s.locationName.trim().isNotEmpty) return s.locationName.trim();
    return 'Участок ${s.id}';
  }

  /// Текстовый статус загруженности: Свободно / Затор / Пробка.
  String _trafficStatusLabel(double? value) {
    if (value == null) return '—';
    if (value <= 30) return 'Свободно';
    if (value <= 60) return 'Затор';
    return 'Пробка';
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final heavy = segments.where((s) => (s.value ?? 0) > 60).length;
    final medium = segments.where((s) {
      final v = s.value ?? 0;
      return v > 30 && v <= 60;
    }).length;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: whiteAppBar(
        'Маршруты',
        actions: [
          if (loading)
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            )
          else
            IconButton(
              icon: const Icon(Icons.refresh_rounded),
              onPressed: _load,
              tooltip: 'Обновить',
            ),
        ],
      ),
      body: Column(
        children: [
          // Карточка: Прогноз загруженности
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 10),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.06),
                    blurRadius: 20,
                    offset: const Offset(0, 6),
                  ),
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.04),
                    blurRadius: 30,
                    offset: const Offset(0, 2),
                  ),
                ],
                border: Border.all(color: AppColors.divider.withOpacity(0.5)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.traffic_rounded,
                            color: AppColors.primary, size: 24),
                      ),
                      const SizedBox(width: 14),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Прогноз загруженности',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w700,
                              color: AppColors.textPrimary,
                              letterSpacing: -0.3,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'г. Астана',
                            style: TextStyle(
                              fontSize: 13,
                              color: AppColors.textSecondary,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 14, vertical: 4),
                          decoration: BoxDecoration(
                            color: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.8),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                                color: Theme.of(context).dividerColor.withOpacity(0.4)),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<int>(
                              value: horizon,
                              isExpanded: true,
                              items: const [
                                DropdownMenuItem(
                                    value: 0, child: Text('Сейчас')),
                                DropdownMenuItem(
                                    value: 30, child: Text('+30 мин')),
                                DropdownMenuItem(
                                    value: 60, child: Text('+60 мин')),
                              ],
                              onChanged: (v) {
                                if (v == null) return;
                                setState(() => horizon = v);
                                _load();
                              },
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 16,
                    runSpacing: 8,
                    children: [
                      _legendChip(const Color(0xFF22C55E), 'Свободно'),
                      _legendChip(const Color(0xFFF97316), 'Затор'),
                      _legendChip(const Color(0xFFEF4444), 'Пробка'),
                    ],
                  ),
                  if (!loading && segments.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Text(
                      'Пробка — $heavy улиц • Затор — $medium улиц',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          // Поиск
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Поиск по улице или названию',
                prefixIcon: const Icon(Icons.search_rounded, size: 22),
                filled: true,
                fillColor: Theme.of(context).cardColor,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: BorderSide.none,
                ),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
              onChanged: (v) => setState(() => query = v),
            ),
          ),
          const SizedBox(height: 12),
          if (error != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFFECACA)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline_rounded,
                        color: Color(0xFFDC2626), size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                        child: Text(error!,
                            style: TextStyle(
                                color: Theme.of(context).brightness == Brightness.dark ? Colors.red.shade200 : const Color(0xFFB91C1C), 
                                fontSize: 13))),
                  ],
                ),
              ),
            ),
          if (error != null) const SizedBox(height: 8),
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
              itemCount: filtered.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, i) {
                final s = filtered[i];
                final v = s.value;
                final color = colorByValue(v);
                final streetName = _streetName(s);
                final statusLabel = _trafficStatusLabel(v);
                return Material(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                  elevation: 0,
                  shadowColor: Colors.black.withOpacity(0.06),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => SegmentMapPage(segment: s),
                        ),
                      );
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: color.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Center(
                              child: Icon(
                                statusLabel == 'Пробка'
                                    ? Icons.traffic_rounded
                                    : statusLabel == 'Затор'
                                        ? Icons.warning_amber_rounded
                                        : Icons.check_circle_outline_rounded,
                                size: 24,
                                color: color,
                              ),
                            ),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  streetName,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w600,
                                    fontSize: 15,
                                    color: AppColors.textPrimary,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                          horizontal: 8, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: color.withOpacity(0.15),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Text(
                                        statusLabel,
                                        style: TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.w600,
                                          color: color,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      'г. Астана',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: AppColors.textSecondary,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          Icon(Icons.chevron_right_rounded,
                              color: AppColors.textSecondary, size: 24),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _legendChip(Color color, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: 6),
        Text(label,
            style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
      ],
    );
  }
}
