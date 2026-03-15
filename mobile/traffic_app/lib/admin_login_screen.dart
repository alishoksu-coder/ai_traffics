import 'dart:ui' as dart_ui;
import 'package:flutter/material.dart';

import 'api.dart';
import 'common.dart';

class AdminLoginScreen extends StatefulWidget {
  const AdminLoginScreen({super.key});

  @override
  State<AdminLoginScreen> createState() => _AdminLoginScreenState();
}

class _AdminLoginScreenState extends State<AdminLoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _loginController = TextEditingController(text: 'admin');
  final _passwordController = TextEditingController();
  final api = ApiClient();
  bool loading = false;
  String? error;

  @override
  void dispose() {
    _loginController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    setState(() {
      error = null;
      loading = true;
    });
    try {
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
                color: const Color(0xFF0D7EA7).withOpacity(0.15),
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
                        color: Colors.white.withOpacity(0.05),
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white.withOpacity(0.1)),
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
                      'Управление системой мониторинга',
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
                            color: Colors.white.withOpacity(0.05),
                            borderRadius: BorderRadius.circular(24),
                            border: Border.all(color: Colors.white.withOpacity(0.1)),
                          ),
                          child: Form(
                            key: _formKey,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                _buildTextField(
                                  controller: _loginController,
                                  label: 'Логин',
                                  icon: Icons.person_outline,
                                ),
                                const SizedBox(height: 16),
                                _buildTextField(
                                  controller: _passwordController,
                                  label: 'Пароль',
                                  icon: Icons.lock_outline,
                                  isPassword: true,
                                  onSubmitted: (_) => _login(),
                                ),
                                if (error != null) _buildError(error!),
                                const SizedBox(height: 24),
                                FilledButton(
                                  onPressed: loading
                                      ? null
                                      : () {
                                          if (_formKey.currentState?.validate() ?? false)
                                            _login();
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
                                      : const Text('Вход в систему'),
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
    Function(String)? onSubmitted,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: isPassword,
      style: const TextStyle(color: Colors.white),
      onFieldSubmitted: onSubmitted,
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.white60),
        prefixIcon: Icon(icon, color: Colors.white60),
        filled: true,
        fillColor: Colors.white.withOpacity(0.05),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.white.withOpacity(0.05)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF0EA5E9), width: 2),
        ),
      ),
      validator: (v) => (v == null || v.isEmpty) ? 'Обязательное поле' : null,
    );
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
      if (mounted)
        setState(() {
          stats = data;
          loading = false;
        });
    } catch (e) {
      if (mounted)
        setState(() {
          error = e.toString();
          loading = false;
        });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Dashboard'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: loading ? null : _load,
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: loading && stats == null
          ? const Center(child: CircularProgressIndicator())
          : _buildDashboard(),
    );
  }

  Widget _buildDashboard() {
    final color = Theme.of(context).textTheme.bodyLarge?.color ?? const Color(0xFF0F172A);
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // Welcome segment
        Row(
          children: [
            Text(
              'Привет, Админ!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: color),
            ),
            Spacer(),
            Icon(Icons.notifications_none, color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.5)),
          ],
        ),
        const SizedBox(height: 24),

        // Main Score Card
        _buildHeroCard(),

        const SizedBox(height: 24),
        Text(
          'Статистика узлов',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: color),
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
            _buildStatBox('Локации', '${stats?['locations_count'] ?? 0}', Icons.place, const Color(0xFF6366F1)),
            _buildStatBox('Сегменты', '${stats?['segments_count'] ?? 0}', Icons.alt_route, const Color(0xFF0EA5E9)),
            _buildStatBox('Транспорт', '${stats?['vehicles_count'] ?? 0}', Icons.directions_car, const Color(0xFFF59E0B)),
            _buildStatBox('Хотспоты', '${stats?['hotspots'] ?? 0}', Icons.local_fire_department, const Color(0xFFEF4444)),
          ],
        ),

        const SizedBox(height: 32),
        Text(
          'Активность системы',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: color),
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
          BoxShadow(color: Colors.black.withOpacity(Theme.of(context).brightness == Brightness.dark ? 0.2 : 0.04), blurRadius: 20, offset: const Offset(0, 10)),
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
                  color: color.withOpacity(0.1),
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
                    Text('Средний балл по городу', style: TextStyle(color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.5), fontSize: 12)),
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
          Text(title, style: TextStyle(fontSize: 12, color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.5), fontWeight: FontWeight.w500)),
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
          _logItem('Симулятор обновлен', '2 мин назад', Icons.sync, Colors.blue),
          const Divider(height: 24),
          _logItem('Обнаружен хотспот #2', '15 мин назад', Icons.warning_amber, Colors.orange),
          const Divider(height: 24),
          _logItem('Сервер API запущен', '1 час назад', Icons.power_settings_new, Colors.green),
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
        Text(time, style: TextStyle(color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.5), fontSize: 12)),
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
      ..color = color.withOpacity(0.5)
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
