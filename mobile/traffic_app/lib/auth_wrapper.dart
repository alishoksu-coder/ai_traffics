import 'package:flutter/material.dart';
import 'package:local_auth/local_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthWrapper extends StatefulWidget {
  final Widget child;
  const AuthWrapper({super.key, required this.child});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  final LocalAuthentication auth = LocalAuthentication();
  bool _isAuthenticated = false;
  bool _isLoading = true;

  String? _pinCode;
  bool _useBiometrics = false;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final prefs = await SharedPreferences.getInstance();
    _useBiometrics = prefs.getBool('useBiometrics') ?? false;
    _pinCode = prefs.getString('pinCode');

    if (!_useBiometrics && _pinCode == null) {
      // Защита не включена
      setState(() {
        _isAuthenticated = true;
        _isLoading = false;
      });
      return;
    }

    if (_useBiometrics) {
      try {
        final didAuthenticate = await auth.authenticate(
          localizedReason: 'Пройдите аутентификацию для доступа к приложению',
          options: const AuthenticationOptions(
            biometricOnly: false,
            useErrorDialogs: true,
            stickyAuth: true,
          ),
        );
        if (didAuthenticate) {
          setState(() {
            _isAuthenticated = true;
            _isLoading = false;
          });
          return;
        }
      } catch (e) {
        // Ошибка биометрии, переходим к пину если он установлен
      }
    }
    
    // Если биометрия не сработала или не включена, но включен ПИН
    if (_pinCode == null) {
        setState(() {
          _isAuthenticated = true;
          _isLoading = false;
        });
        return;
    }
    
    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_isAuthenticated) {
      return widget.child;
    }

    return _PinCodeScreen(
      correctPin: _pinCode,
      onSuccess: () {
        setState(() {
          _isAuthenticated = true;
        });
      },
    );
  }
}

class _PinCodeScreen extends StatefulWidget {
  final String? correctPin;
  final VoidCallback onSuccess;
  
  const _PinCodeScreen({required this.correctPin, required this.onSuccess});

  @override
  State<_PinCodeScreen> createState() => _PinCodeScreenState();
}

class _PinCodeScreenState extends State<_PinCodeScreen> {
  String _enteredPin = '';

  void _onNumberTap(String number) {
    if (_enteredPin.length < 4) {
      setState(() {
        _enteredPin += number;
      });
      if (_enteredPin.length == 4) {
        if (widget.correctPin == null || _enteredPin == widget.correctPin) {
          widget.onSuccess();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Неверный PIN-код'),
              backgroundColor: Colors.red,
            ),
          );
          setState(() {
            _enteredPin = '';
          });
        }
      }
    }
  }

  void _onDeleteTap() {
    if (_enteredPin.isNotEmpty) {
      setState(() {
        _enteredPin = _enteredPin.substring(0, _enteredPin.length - 1);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    const primaryColor = Color(0xFF4C45E5);
    
    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF0F172A) : const Color(0xFFF4F7FA),
      body: SafeArea(
        child: Column(
          children: [
            const Spacer(),
            const Icon(Icons.lock_outline_rounded, size: 72, color: primaryColor),
            const SizedBox(height: 24),
            Text(
              'Введите PIN-код', 
              style: TextStyle(
                fontSize: 22, 
                fontWeight: FontWeight.bold,
                color: isDark ? Colors.white : Colors.black87,
              )
            ),
            const SizedBox(height: 48),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(4, (index) {
                bool isFilled = index < _enteredPin.length;
                return Container(
                  margin: const EdgeInsets.symmetric(horizontal: 14),
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isFilled ? primaryColor : Colors.transparent,
                    border: Border.all(color: isFilled ? primaryColor : (isDark ? Colors.white30 : Colors.black26), width: 2),
                  ),
                );
              }),
            ),
            const Spacer(),
            // Кнопки цифр
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 48),
              child: GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  childAspectRatio: 1.2,
                  crossAxisSpacing: 24,
                  mainAxisSpacing: 24,
                ),
                itemCount: 12,
                itemBuilder: (context, index) {
                  if (index == 9) return const SizedBox(); 
                  if (index == 11) {
                    return InkWell(
                      onTap: _onDeleteTap,
                      customBorder: const CircleBorder(),
                      child: Center(
                        child: Icon(Icons.backspace_outlined, size: 28, color: isDark ? Colors.white : Colors.black87)
                      ),
                    );
                  }
                  final number = index == 10 ? '0' : '${index + 1}';
                  return InkWell(
                    onTap: () => _onNumberTap(number),
                    customBorder: const CircleBorder(),
                    child: Container(
                       decoration: BoxDecoration(
                         shape: BoxShape.circle,
                         color: isDark ? Colors.white.withOpacity(0.04) : Colors.black.withOpacity(0.03),
                       ),
                       child: Center(
                        child: Text(
                          number, 
                          style: TextStyle(
                            fontSize: 32, 
                            fontWeight: FontWeight.w500,
                            color: isDark ? Colors.white : Colors.black87,
                          )
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 54),
          ],
        ),
      ),
    );
  }
}
