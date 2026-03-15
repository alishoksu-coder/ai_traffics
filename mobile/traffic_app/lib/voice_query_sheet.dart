import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:permission_handler/permission_handler.dart';

import 'api.dart';
import 'common.dart';

/// Результат текстового/AI‑запроса «Куда доехать»: точка A (текущая) и B (назначение).
class VoiceQueryResult {
  final LatLng origin;
  final LatLng destination;
  final String destinationName;

  const VoiceQueryResult({
    required this.origin,
    required this.destination,
    required this.destinationName,
  });
}

/// Нижняя панель: поле ввода + кнопка «Поехать». По результату возвращает [VoiceQueryResult].
void showVoiceQuerySheet(BuildContext context,
    {required void Function(VoiceQueryResult) onResult}) {
  showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    builder: (ctx) => _VoiceQuerySheetContent(
      onResult: (r) {
        Navigator.of(ctx).pop();
        onResult(r);
      },
      onCancel: () => Navigator.of(ctx).pop(),
    ),
  );
}

class _VoiceQuerySheetContent extends StatefulWidget {
  final void Function(VoiceQueryResult) onResult;
  final VoidCallback onCancel;

  const _VoiceQuerySheetContent(
      {required this.onResult, required this.onCancel});

  @override
  State<_VoiceQuerySheetContent> createState() =>
      _VoiceQuerySheetContentState();
}

class _VoiceQuerySheetContentState extends State<_VoiceQuerySheetContent> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  static const MethodChannel _speechChannel = MethodChannel('voice_recognizer');
  bool _isListening = false;
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  Future<void> _startListening() async {
    setState(() {
      _error = null;
      _isListening = true;
    });
    try {
      // Запрашиваем разрешение на микрофон перед вызовом нативного распознавания
      var status = await Permission.microphone.status;
      if (!status.isGranted) {
        status = await Permission.microphone.request();
      }
      if (!status.isGranted) {
        if (mounted) {
          setState(() {
            _error = 'Разрешите доступ к микрофону в настройках приложения';
            _isListening = false;
          });
        }
        return;
      }

      final text = await _speechChannel.invokeMethod<String>('startListening');
      if (!mounted) return;
      if (text != null && text.isNotEmpty) {
        setState(() {
          _controller.text = text;
          _controller.selection =
              TextSelection.collapsed(offset: _controller.text.length);
        });
      }
    } on PlatformException catch (e) {
      if (mounted) {
        setState(() {
          _error = e.message ?? 'Ошибка распознавания речи';
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isListening = false;
        });
      }
    }
  }

  Future<void> _submit() async {
    final query = _controller.text.trim();
    if (query.isEmpty) {
      setState(() => _error = 'Введите адрес или название места');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final place = await getPlaceFromQuery(query);

      LocationPermission perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) {
        perm = await Geolocator.requestPermission();
      }
      if (perm == LocationPermission.deniedForever) {
        throw Exception('Доступ к геолокации запрещён. Включите в настройках.');
      }
      if (perm == LocationPermission.denied) {
        throw Exception('Нужен доступ к геолокации для маршрута от вас.');
      }

      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.medium,
      );
      if (!mounted) return;

      widget.onResult(VoiceQueryResult(
        origin: LatLng(pos.latitude, pos.longitude),
        destination: LatLng(place.lat, place.lon),
        destinationName: place.formattedAddress,
      ));
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Icon(Icons.navigation_rounded,
                    color: AppColors.primary, size: 26),
              ),
              const SizedBox(width: 14),
              const Expanded(
                child: Text(
                  'Куда доехать?',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                    letterSpacing: -0.3,
                  ),
                ),
              ),
              IconButton.filled(
                style: IconButton.styleFrom(
                  backgroundColor: AppColors.surfaceVariant,
                  foregroundColor: AppColors.textSecondary,
                ),
                icon: const Icon(Icons.close_rounded),
                onPressed: widget.onCancel,
              ),
            ],
          ),
          const SizedBox(height: 20),
          TextField(
            controller: _controller,
            focusNode: _focusNode,
            decoration: InputDecoration(
              hintText: 'Хан Шатыр, проспект Республики...',
              prefixIcon: const Icon(Icons.search_rounded,
                  color: AppColors.textSecondary),
              suffixIcon: IconButton(
                icon: Icon(
                  _isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
                  color: _isListening
                      ? Colors.red.shade400
                      : AppColors.textSecondary,
                ),
                onPressed: _isListening ? null : _startListening,
                tooltip: 'Голосовой ввод',
              ),
            ),
            textInputAction: TextInputAction.done,
            onSubmitted: (_) => _submit(),
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                children: [
                  Icon(Icons.error_outline_rounded,
                      size: 18, color: Colors.red.shade700),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _error!,
                      style:
                          TextStyle(color: Colors.red.shade700, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 20),
          FilledButton.icon(
            onPressed: _loading ? null : _submit,
            icon: _loading
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.directions_car_rounded, size: 22),
            label: Text(_loading ? 'Построение маршрута...' : 'Поехать'),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              backgroundColor: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }
}
