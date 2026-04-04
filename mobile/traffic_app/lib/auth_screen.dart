import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'app.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  bool _isLogin = true;
  bool _isLoading = false;
  bool _obscurePassword = true;

  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  
  // Registration extras
  final _firstNameCtrl = TextEditingController();
  final _lastNameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _dobCtrl = TextEditingController(); // Date of birth

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passCtrl.dispose();
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _phoneCtrl.dispose();
    _dobCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final email = _emailCtrl.text.trim();
    final pass = _passCtrl.text.trim();

    if (email.isEmpty || pass.isEmpty) {
      _showError('Барлық міндетті өрістерді толтырыңыз (Email және құпия сөз)');
      return;
    }

    setState(() => _isLoading = true);
    try {
      if (_isLogin) {
        // Логин
        await Supabase.instance.client.auth.signInWithPassword(
          email: email,
          password: pass,
        );
      } else {
        // Регистрация
        final authRes = await Supabase.instance.client.auth.signUp(
          email: email,
          password: pass,
          data: {
            'first_name': _firstNameCtrl.text.trim(),
            'last_name': _lastNameCtrl.text.trim(),
            'phone': _phoneCtrl.text.trim(),
            'birth_date': _dobCtrl.text.trim(),
          },
        );

        final user = authRes.user;
        if (user != null) {
          // Пытаемся сохранить профиль. Если RLS заблокирует — не страшно,
          // так как мы уже надежно сохранили эти данные внутри auth.users через параметр `data` выше.
          try {
            await Supabase.instance.client.from('profiles').upsert({
              'id': user.id,
              'first_name': _firstNameCtrl.text.trim(),
              'last_name': _lastNameCtrl.text.trim(),
              'phone': _phoneCtrl.text.trim(),
              'birth_date': _dobCtrl.text.trim(),
            });
          } catch (e) {
            debugPrint('RLS салдарынан профиль сақталмады, бірақ аккаунт сәтті құрылды: $e');
          }
        }
      }

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeShell()),
        );
      }
    } on AuthException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('Қате орын алды: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg),
      backgroundColor: Colors.redAccent,
    ));
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0F172A) : Colors.white;
    
    return Scaffold(
      backgroundColor: bgColor,
      body: SafeArea(
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: _isLogin ? _buildLogin(isDark) : _buildRegister(isDark),
        ),
      ),
    );
  }

  Widget _buildLogin(bool isDark) {
    final primary = const Color(0xFF5A52FF);
    final textDark = isDark ? Colors.white : const Color(0xFF111827);
    final textSoft = isDark ? Colors.white60 : const Color(0xFF6B7280);

    return SingleChildScrollView(
      key: const ValueKey('login'),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
      physics: const BouncingScrollPhysics(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const SizedBox(height: 48),
          // Обновленный логотип
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: primary,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: primary.withOpacity(0.3),
                  blurRadius: 24,
                  offset: const Offset(0, 10),
                )
              ],
            ),
            child: const Icon(Icons.radar_rounded, color: Colors.white, size: 40),
          ),
          const SizedBox(height: 48),
          
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Қош\nкелдіңіз!',
                style: TextStyle(fontSize: 36, fontWeight: FontWeight.w800, color: textDark, height: 1.1, letterSpacing: -1),
              ),
              const SizedBox(height: 12),
              Text(
                'Traffic AI-мен жұмысты жалғастыру үшін жүйеге кіріңіз',
                style: TextStyle(fontSize: 15, color: textSoft),
              ),
              const SizedBox(height: 32),

              _buildCustomField(_emailCtrl, 'Email', Icons.mail_outline_rounded, isDark: isDark),
              const SizedBox(height: 16),
              _buildCustomField(_passCtrl, 'Құпия сөз', Icons.lock_outline_rounded, isPassword: true, isDark: isDark),
              
              const SizedBox(height: 32),

              SizedBox(
                width: double.infinity,
                height: 56,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: primary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  onPressed: _isLoading ? null : _submit,
                  child: _isLoading
                      ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Text('Кіру', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 64),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Аккаунтыңыз жоқ па? ', style: TextStyle(color: textSoft, fontSize: 14)),
              GestureDetector(
                onTap: () => setState(() => _isLogin = false),
                child: Text('Тіркелу', style: TextStyle(color: primary, fontWeight: FontWeight.bold, fontSize: 14)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRegister(bool isDark) {
    final primary = const Color(0xFF5A52FF);
    final textDark = isDark ? Colors.white : const Color(0xFF111827);
    final textSoft = isDark ? Colors.white60 : const Color(0xFF6B7280);

    return SingleChildScrollView(
      key: const ValueKey('register'),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      physics: const BouncingScrollPhysics(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          IconButton(
            onPressed: () => setState(() => _isLogin = true),
            icon: Icon(Icons.arrow_back_rounded, color: textDark),
            padding: EdgeInsets.zero,
            alignment: Alignment.centerLeft,
          ),
          const SizedBox(height: 16),
          Text(
            'Аккаунт\nқұру',
            style: TextStyle(fontSize: 36, fontWeight: FontWeight.w800, color: textDark, height: 1.1, letterSpacing: -1),
          ),
          const SizedBox(height: 12),
          Text(
            'Бізге қосылыңыз және ақылды маршруттарды құрыңыз',
            style: TextStyle(fontSize: 15, color: textSoft),
          ),
          const SizedBox(height: 32),

          Text('ЖЕКЕ ДЕРЕКТЕР', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.5, color: primary)),
          const SizedBox(height: 16),
          _buildCustomField(_firstNameCtrl, 'Аты', Icons.person_outline_rounded, isDark: isDark),
          const SizedBox(height: 12),
          _buildCustomField(_lastNameCtrl, 'Тегі', Icons.badge_outlined, isDark: isDark),
          const SizedBox(height: 12),
          _buildCustomField(_dobCtrl, 'Туған күні', Icons.calendar_today_outlined, isDark: isDark),
          const SizedBox(height: 12),
          _buildCustomField(_phoneCtrl, 'Телефон нөмірі', Icons.phone_outlined, type: TextInputType.phone, isDark: isDark),
          
          const SizedBox(height: 32),
          Text('КІРУ ДЕРЕКТЕРІ', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.5, color: primary)),
          const SizedBox(height: 16),
          _buildCustomField(_emailCtrl, 'Email', Icons.mail_outline_rounded, type: TextInputType.emailAddress, isDark: isDark),
          const SizedBox(height: 12),
          _buildCustomField(_passCtrl, 'Құпия сөз', Icons.lock_outline_rounded, isPassword: true, isDark: isDark),
          
          const SizedBox(height: 32),

          SizedBox(
            width: double.infinity,
            height: 56,
            child: FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: primary,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              ),
              onPressed: _isLoading ? null : _submit,
              child: _isLoading
                  ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('Тіркелу', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
            ),
          ),
          
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Аккаунтыңыз бар ма? ', style: TextStyle(color: textSoft, fontSize: 13)),
              GestureDetector(
                onTap: () => setState(() => _isLogin = true),
                child: Text('Кіру', style: TextStyle(color: primary, fontWeight: FontWeight.bold, fontSize: 14)),
              ),
            ],
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildCustomField(TextEditingController ctrl, String hint, IconData icon, {bool isPassword = false, TextInputType? type, required bool isDark}) {
    final fillColor = isDark ? const Color(0xFF1E293B) : const Color(0xFFF4F4F6);
    final iconColor = isDark ? Colors.white54 : const Color(0xFF4B5563);
    final textColor = isDark ? Colors.white : const Color(0xFF111827);

    return Container(
      decoration: BoxDecoration(
        color: fillColor,
        borderRadius: BorderRadius.circular(16),
      ),
      child: TextField(
        controller: ctrl,
        keyboardType: type,
        obscureText: isPassword && _obscurePassword,
        style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: textColor),
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: TextStyle(fontSize: 15, fontWeight: FontWeight.w400, color: iconColor),
          prefixIcon: Icon(icon, color: iconColor, size: 22),
          suffixIcon: isPassword 
            ? IconButton(
                icon: Icon(_obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined, color: iconColor, size: 20),
                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
              )
            : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
        ),
      ),
    );
  }
}
