import 'dart:ui' as dart_ui;
import 'package:flutter/material.dart';

import 'api.dart';

class AdminLoginScreen extends StatefulWidget {
  const AdminLoginScreen({super.key});

  @override
  State<AdminLoginScreen> createState() => _AdminLoginScreenState();
}

class _AdminLoginScreenState extends State<AdminLoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _loginController = TextEditingController(text: 'admin');
  final _passwordController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _dobController = TextEditingController();
  
  final api = ApiClient();
  bool loading = false;
  String? error;
  bool _isLogin = true;

  @override
  void dispose() {
    _loginController.dispose();
    _passwordController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _dobController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      error = null;
      loading = true;
    });
    try {
      if (_isLogin) {
        final token = await api.adminLogin(
          _loginController.text.trim(),
          _passwordController.text,
        );
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => AdminDashboardScreen(token: token),
          ),
        );
      } else {
        await api.adminRegister(
          login: _loginController.text.trim(),
          password: _passwordController.text,
          firstName: _firstNameController.text.trim(),
          lastName: _lastNameController.text.trim(),
          phone: _phoneController.text.trim(),
          birthDate: _dobController.text.trim(),
        );
        if (!mounted) return;
        
        setState(() {
          error = 'Сәтті өтті! Егер растау қосылған болса – поштаңызды тексеріңіз.';
          loading = false;
        });
        
        // Показываем зеленый SnackBar
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Тіркеу сәтті өтті. Енді сіз жүйеге кіре аласыз (поштаны растаған соң).'),
            backgroundColor: Colors.green,
          ),
        );
        
        setState(() {
          _isLogin = true;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString().replaceFirst('Exception: ', '');
          loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A), // Dark slate background
      body: Stack(
        children: [
          // Background Glows
          Positioned(
            top: -100,
            right: -50,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFF0D7EA7).withValues(alpha: 0.15),
              ),
              child: BackdropFilter(
                filter: dart_ui.ImageFilter.blur(sigmaX: 80, sigmaY: 80),
                child: Container(color: Colors.transparent),
              ),
            ),
          ),
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(32),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Logo with Glass effect
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.05),
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
                      ),
                      child: ClipOval(
                        child: Image.asset(
                          'assets/images/logo.png',
                          width: 100,
                          height: 100,
                          errorBuilder: (context, _, __) => const Icon(
                            Icons.admin_panel_settings,
                            size: 100,
                            color: Colors.white24,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Traffic AI Admin',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const Text(
                      'Мониторинг жүйесін басқару',
                      style: TextStyle(
                        color: Colors.white60,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 48),

                    // Glass Login Card
                    ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: BackdropFilter(
                        filter: dart_ui.ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                        child: Container(
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.05),
                            borderRadius: BorderRadius.circular(24),
                            border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
                          ),
                          child: Form(
                            key: _formKey,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                if (!_isLogin) ...[
                                  _buildTextField(
                                    controller: _firstNameController,
                                    label: 'Аты',
                                    icon: Icons.person_outline,
                                  ),
                                  const SizedBox(height: 16),
                                  _buildTextField(
                                    controller: _lastNameController,
                                    label: 'Тегі',
                                    icon: Icons.badge_outlined,
                                  ),
                                  const SizedBox(height: 16),
                                  _buildTextField(
                                    controller: _phoneController,
                                    label: 'Телефон нөмірі',
                                    icon: Icons.phone_android,
                                  ),
                                  const SizedBox(height: 16),
                                  _buildTextField(
                                    controller: _dobController,
                                    label: 'Туған күні',
                                    icon: Icons.calendar_today_outlined,
                                    readOnly: true,
                                    onTap: _selectDate,
                                  ),
                                  const SizedBox(height: 16),
                                ],
                                _buildTextField(
                                  controller: _loginController,
                                  label: 'Email / Логин',
                                  icon: Icons.person_outline,
                                ),
                                const SizedBox(height: 16),
                                _buildTextField(
                                  controller: _passwordController,
                                  label: 'Құпия сөз',
                                  icon: Icons.lock_outline,
                                  isPassword: true,
                                  onSubmitted: (_) => _submit(),
                                ),
                                if (error != null) _buildError(error!),
                                const SizedBox(height: 24),
                                FilledButton(
                                  onPressed: loading
                                      ? null
                                      : () {
                                          if (_formKey.currentState?.validate() ?? false)
                                            _submit();
                                        },
                                  style: FilledButton.styleFrom(
                                    backgroundColor: const Color(0xFF0EA5E9),
                                    padding: const EdgeInsets.symmetric(vertical: 18),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                                  ),
                                  child: loading
                                      ? const SizedBox(
                                          height: 24,
                                          width: 24,
                                          child: CircularProgressIndicator(
                                              strokeWidth: 2, color: Colors.white))
                                      : Text(_isLogin ? 'Жүйеге кіру' : 'Тіркелу'),
                                ),
                                const SizedBox(height: 16),
                                TextButton(
                                  onPressed: () {
                                    setState(() {
                                      _isLogin = !_isLogin;
                                      error = null;
                                      if (!_isLogin) {
                                        _loginController.clear();
                                      } else {
                                        _loginController.text = 'admin';
                                      }
                                    });
                                  },
                                  child: Text(
                                    _isLogin ? 'Аккаунтыңыз жоқ па? Тіркелу' : 'Аккаунтыңыз бар ма? Кіру',
                                    style: const TextStyle(color: Colors.white70),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool isPassword = false,
    bool readOnly = false,
    VoidCallback? onTap,
    Function(String)? onSubmitted,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: isPassword,
      readOnly: readOnly,
      onTap: onTap,
      style: const TextStyle(color: Colors.white),
      onFieldSubmitted: onSubmitted,
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.white60),
        prefixIcon: Icon(icon, color: Colors.white60),
        filled: true,
        fillColor: Colors.white.withValues(alpha: 0.05),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.05)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF0EA5E9), width: 2),
        ),
      ),
      validator: (v) => (v == null || v.isEmpty) ? 'Міндетті өріс' : null,
    );
  }

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime(2000),
      firstDate: DateTime(1950),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.dark(
              primary: Color(0xFF0EA5E9),
              onPrimary: Colors.white,
              surface: Color(0xFF1E293B),
              onSurface: Colors.white,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        _dobController.text =
            "${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}";
      });
    }
  }

  Widget _buildError(String msg) {
    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Text(
        msg,
        style: const TextStyle(color: Colors.redAccent, fontSize: 13),
        textAlign: TextAlign.center,
      ),
    );
  }
}

class AdminDashboardScreen extends StatefulWidget {
  final String token;

  const AdminDashboardScreen({super.key, required this.token});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  final api = ApiClient();
  bool loading = true;
  String? error;
  Map<String, dynamic>? stats;
  String adminName = 'Админ';

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
      final data = await api.adminDashboard(widget.token);
      if (mounted) {
        setState(() {
          adminName = data['admin_name'] as String? ?? 'Админ';
          stats = data['metrics'] as Map<String, dynamic>?;
          loading = false;
        });
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

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = const Color(0xFF0EA5E9); // Синий акцент для админки
    final color = Theme.of(context).textTheme.bodyLarge?.color ?? const Color(0xFF0F172A);

    return Scaffold(
      backgroundColor: primaryColor,
      body: Column(
        children: [
          // Синяя шапка
          Container(
            padding: EdgeInsets.only(
              top: MediaQuery.of(context).padding.top + 16,
              left: 24,
              right: 24,
              bottom: 40,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        GestureDetector(
                          onTap: () => Navigator.pop(context),
                          child: Container(
                            padding: const EdgeInsets.only(right: 16, bottom: 8, top: 8),
                            child: const Icon(Icons.arrow_back_rounded, color: Colors.white, size: 28),
                          ),
                        ),
                        Text(
                          adminName,
                          style: const TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.w800,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Traffic AI Жүйесі',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.white.withValues(alpha: 0.8),
                      ),
                    ),
                  ],
                ),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: IconButton(
                    icon: loading
                        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Icon(Icons.refresh_rounded, color: Colors.white),
                    onPressed: loading ? null : _load,
                    tooltip: 'Жаңарту',
                  ),
                ),
              ],
            ),
          ),
          
          // Тело с карточками
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF0F172A) : const Color(0xFFF4F7FA),
                borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
              ),
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
                child: loading && stats == null
                  ? const Center(child: CircularProgressIndicator())
                  : _buildDashboard(color),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboard(Color textColor) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 32, 20, 100),
      physics: const BouncingScrollPhysics(),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Жиынтық',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: textColor),
            ),
            Icon(Icons.dashboard_rounded, color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.5)),
          ],
        ),
        const SizedBox(height: 16),

        // Main Score Card
        _buildHeroCard(),

        const SizedBox(height: 24),
        Text(
          'Түйіндер статистикасы',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: textColor),
        ),
        const SizedBox(height: 16),


        // Stats Grid
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 1.3,
          children: [
            _buildStatBox('Локациялар', '${stats?['locations_count'] ?? 0}', Icons.place, const Color(0xFF6366F1)),
            _buildStatBox('Сегменттер', '${stats?['segments_count'] ?? 0}', Icons.alt_route, const Color(0xFF0EA5E9)),
            _buildStatBox('Көліктер', '${stats?['vehicles_count'] ?? 0}', Icons.directions_car, const Color(0xFFF59E0B)),
            _buildStatBox('Хотспоттар', '${stats?['hotspots'] ?? 0}', Icons.local_fire_department, const Color(0xFFEF4444)),
          ],
        ),

        const SizedBox(height: 32),
        Text(
          'Жүйе белсенділігі',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: textColor),
        ),
        const SizedBox(height: 12),
        _buildActivityLog(),
        const SizedBox(height: 40),
      ],
    );
  }

  Widget _buildHeroCard() {
    final score = stats?['traffic_score'] ?? 0;
    final color = score <= 3 ? const Color(0xFF10B981) : (score <= 6 ? const Color(0xFFF59E0B) : const Color(0xFFEF4444));

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: Theme.of(context).brightness == Brightness.dark ? 0.2 : 0.04), blurRadius: 20, offset: const Offset(0, 10)),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Text(
                    '$score',
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: color),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Global Traffic Index', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
                    Text('Қала бойынша орташа балл', style: TextStyle(color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.5), fontSize: 12)),
                  ],
                ),
              ),
              const Icon(Icons.trending_up, color: Colors.green),
            ],
          ),
          const SizedBox(height: 24),
          // Fake sparkline
          _buildFakeChart(color),
        ],
      ),
    );
  }

  Widget _buildFakeChart(Color color) {
    return SizedBox(
      height: 60,
      width: double.infinity,
      child: CustomPaint(
        painter: _SparklinePainter(color),
      ),
    );
  }

  Widget _buildStatBox(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 12),
          Text(value, style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: color)),
          Text(title, style: TextStyle(fontSize: 12, color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.5), fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _buildActivityLog() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: Theme.of(context).cardColor, borderRadius: BorderRadius.circular(24)),
      child: Column(
        children: [
          _logItem('Симулятор жаңартылды', '2 мин бұрын', Icons.sync, Colors.blue),
          const Divider(height: 24),
          _logItem('Хотспот #2 табылды', '15 мин бұрын', Icons.warning_amber, Colors.orange),
          const Divider(height: 24),
          _logItem('API сервер іске қосылды', '1 сағат бұрын', Icons.power_settings_new, Colors.green),
        ],
      ),
    );
  }

  Widget _logItem(String title, String time, IconData icon, Color color) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 12),
        Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14))),
        Text(time, style: TextStyle(color: Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.5), fontSize: 12)),
      ],
    );
  }
}

class _SparklinePainter extends CustomPainter {
  final Color color;
  _SparklinePainter(this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withValues(alpha: 0.5)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path();
    path.moveTo(0, size.height * 0.7);
    path.quadraticBezierTo(size.width * 0.2, size.height * 0.3, size.width * 0.4, size.height * 0.6);
    path.quadraticBezierTo(size.width * 0.6, size.height * 0.9, size.width * 0.8, size.height * 0.2);
    path.lineTo(size.width, size.height * 0.5);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
