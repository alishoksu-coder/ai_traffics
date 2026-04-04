import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:local_auth/local_auth.dart';

class SecuritySettingsScreen extends StatefulWidget {
  const SecuritySettingsScreen({super.key});

  @override
  State<SecuritySettingsScreen> createState() => _SecuritySettingsScreenState();
}

class _SecuritySettingsScreenState extends State<SecuritySettingsScreen> {
  bool _useBiometrics = false;
  String? _pinCode;
  final LocalAuthentication auth = LocalAuthentication();

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _useBiometrics = prefs.getBool('useBiometrics') ?? false;
      _pinCode = prefs.getString('pinCode');
    });
  }

  Future<void> _toggleBiometrics(bool value) async {
    if (value) {
      bool canCheckBiometrics = await auth.canCheckBiometrics;
      bool isDeviceSupported = await auth.isDeviceSupported();
      if (!canCheckBiometrics || !isDeviceSupported) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('К сожалению, биометрия не поддерживается на этом устройстве.'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('useBiometrics', value);
    setState(() {
      _useBiometrics = value;
    });
  }

  Future<void> _setPin() async {
    final result = await showDialog<String>(
      context: context,
      builder: (context) => const _PinSetupDialog(),
    );
    if (result != null && result.length == 4) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('pinCode', result);
      setState(() {
        _pinCode = result;
      });
      if (mounted) {
         ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('PIN-код успешно установлен!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  Future<void> _removePin() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('pinCode');
    setState(() {
      _pinCode = null;
    });
    if (mounted) {
         ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('PIN-код удален'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = const Color(0xFF4C45E5);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Кибербезопасность'),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'ЗАЩИТА ВХОДА',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w800,
              letterSpacing: 1.5,
              color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.4),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isDark ? Colors.white.withOpacity(0.08) : Colors.black.withOpacity(0.06),
              ),
            ),
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Вход по FaceID / Отпечатку', style: TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: const Text('Использовать встроенную защиту'),
                  value: _useBiometrics,
                  onChanged: _toggleBiometrics,
                  activeColor: primaryColor,
                  secondary: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: primaryColor.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(Icons.fingerprint_rounded, color: primaryColor),
                  ),
                ),
                Divider(height: 1, indent: 64, color: Theme.of(context).dividerColor.withOpacity(0.5)),
                ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.amber.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.password_rounded, color: Colors.amber),
                  ),
                  title: Text(_pinCode == null ? 'Установить PIN-код' : 'Изменить PIN-код', style: const TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Text(_pinCode == null ? 'Резервный пароль из 4 цифр' : 'PIN-код защищает ваш вход'),
                  onTap: _setPin,
                  trailing: Icon(Icons.chevron_right_rounded, color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.3)),
                ),
                if (_pinCode != null) ...[
                  Divider(height: 1, indent: 64, color: Theme.of(context).dividerColor.withOpacity(0.5)),
                  ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.delete_outline_rounded, color: Colors.red),
                    ),
                    title: const Text('Удалить PIN-код', style: TextStyle(color: Colors.red, fontWeight: FontWeight.w600)),
                    onTap: _removePin,
                  ),
                ]
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PinSetupDialog extends StatefulWidget {
  const _PinSetupDialog();

  @override
  State<_PinSetupDialog> createState() => _PinSetupDialogState();
}

class _PinSetupDialogState extends State<_PinSetupDialog> {
  final _controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Новый PIN-код', style: TextStyle(fontWeight: FontWeight.bold)),
      content: TextField(
        controller: _controller,
        keyboardType: TextInputType.number,
        maxLength: 4,
        obscureText: true,
        autofocus: true,
        style: const TextStyle(fontSize: 24, letterSpacing: 10),
        textAlign: TextAlign.center,
        decoration: InputDecoration(
          hintText: '----',
          counterText: '',
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context), 
          child: const Text('Отмена')
        ),
        FilledButton(
          onPressed: () {
            if (_controller.text.length == 4) {
              Navigator.pop(context, _controller.text);
            }
          },
          child: const Text('Сохранить'),
        ),
      ],
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
    );
  }
}
