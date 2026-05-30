import 'package:flutter/material.dart';

import '../../services/api_client.dart';
import '../../models/models.dart';

class FriendsScreen extends StatefulWidget {
  final VoidCallback? onShowOnMap;

  const FriendsScreen({super.key, this.onShowOnMap});

  @override
  State<FriendsScreen> createState() => _FriendsScreenState();
}

class _FriendsScreenState extends State<FriendsScreen>
    with SingleTickerProviderStateMixin {
  final api = ApiClient();
  late TabController _tabController;

  bool loading = true;
  String? error;

  List<Friend> friends = [];
  List<Map<String, dynamic>> requests = [];
  List<Map<String, dynamic>> allUsers = [];
  List<Map<String, dynamic>> searchResults = [];

  final TextEditingController _searchCtrl = TextEditingController();
  bool isSearching = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadAll();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadAll() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final results = await Future.wait([
        api.getFriendsWithStatus(),
        api.getFriendRequests(),
        api.getAllUsers(),
      ]);

      if (mounted) {
        setState(() {
          friends = results[0] as List<Friend>;
          requests = results[1] as List<Map<String, dynamic>>;
          allUsers = results[2] as List<Map<String, dynamic>>;
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

  void _onSearch(String query) async {
    if (query.isEmpty) {
      setState(() {
        isSearching = false;
        searchResults = [];
      });
      return;
    }

    setState(() => isSearching = true);
    final list = await api.searchUsers(query);
    if (mounted) {
      setState(() {
        searchResults = list;
        isSearching = false;
      });
    }
  }

  Future<void> _addOrConfirm(String id, String name) async {
    try {
      await api.addFriendById(id, name);
      _loadAll();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Сұраныс жіберілді: $name')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Қате: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    const primaryColor = Color(0xFF4C45E5);

    return Scaffold(
      backgroundColor:
          isDark ? const Color(0xFF0F172A) : const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        title: const Text('Қауымдастық',
            style: TextStyle(fontWeight: FontWeight.w800, fontSize: 22)),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync_rounded),
            onPressed: _loadAll,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          indicatorWeight: 4,
          labelStyle:
              const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          unselectedLabelStyle:
              const TextStyle(fontWeight: FontWeight.w400, fontSize: 13),
          tabs: [
            Tab(text: 'ДОСТАР (${friends.where((f) => f.isConfirmed).length})'),
            Tab(text: 'СҰРАНЫСТАР (${requests.length})'),
            const Tab(text: 'ТҮГЕЛІ'),
          ],
        ),
      ),
      body: Column(
        children: [
          _buildSearchBar(isDark),
          Expanded(
            child: loading && friends.isEmpty && requests.isEmpty
                ? const Center(
                    child: CircularProgressIndicator(color: Color(0xFF4C45E5)))
                : TabBarView(
                    controller: _tabController,
                    children: [
                      _buildFriendsTab(isDark),
                      _buildRequestsTab(isDark),
                      _buildDiscoverTab(isDark),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar(bool isDark) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      color: const Color(0xFF4C45E5),
      child: TextField(
        controller: _searchCtrl,
        onChanged: _onSearch,
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          hintText: 'Есім немесе Email бойынша іздеу...',
          hintStyle:
              TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 14),
          prefixIcon: const Icon(Icons.search_rounded, color: Colors.white70),
          suffixIcon: _searchCtrl.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.close_rounded, color: Colors.white70),
                  onPressed: () {
                    _searchCtrl.clear();
                    _onSearch('');
                  },
                )
              : null,
          filled: true,
          fillColor: Colors.white.withValues(alpha: 0.15),
          contentPadding: const EdgeInsets.symmetric(vertical: 0),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
        ),
      ),
    );
  }

  Widget _buildFriendsTab(bool isDark) {
    final confirmed = friends.where((f) => f.isConfirmed).toList();
    final requested = friends.where((f) => !f.isConfirmed).toList();

    if (confirmed.isEmpty && requested.isEmpty) {
      return _buildEmptyState(
        Icons.people_outline_rounded,
        'Достар тізімі бос',
        'Әзірге ешкімді қоспағансыз. «Түгелі» бөліміне өтіп, таныстарды табыңыз!',
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (widget.onShowOnMap != null && confirmed.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 20),
            child: ElevatedButton.icon(
              onPressed: widget.onShowOnMap,
              icon: const Icon(Icons.map_rounded),
              label: const Text('БАРЛЫҒЫН КАРТАДА КӨРУ'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF4C45E5),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
                elevation: 4,
                shadowColor: const Color(0xFF4C45E5).withValues(alpha: 0.4),
              ),
            ),
          ),
        if (confirmed.isNotEmpty) ...[
          const _SectionHeader(title: 'МЕНІҢ ДОСТАРЫМ'),
          ...confirmed.map((f) => _FriendTile(friend: f, isDark: isDark)),
          const SizedBox(height: 24),
        ],
        if (requested.isNotEmpty) ...[
          const _SectionHeader(title: 'КҮТУДЕГІ СҰРАНЫСТАР'),
          ...requested.map(
              (f) => _FriendTile(friend: f, isDark: isDark, isPending: true)),
        ],
      ],
    );
  }

  Widget _buildRequestsTab(bool isDark) {
    if (requests.isEmpty) {
      return _buildEmptyState(
        Icons.notification_important_outlined,
        'Жаңа сұраныстар жоқ',
        'Сізге ешкім достыққа өтініш жібермеген. Өзіңіз бастама көтеріп көріңіз!',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: requests.length,
      itemBuilder: (ctx, i) {
        final r = requests[i];
        return _UserRequestTile(
          user: r,
          isDark: isDark,
          onConfirm: () => _addOrConfirm(r['id'], r['name']),
        );
      },
    );
  }

  Widget _buildDiscoverTab(bool isDark) {
    final list = _searchCtrl.text.isEmpty ? allUsers : searchResults;

    if (list.isEmpty) {
      return _buildEmptyState(
        Icons.search_off_rounded,
        'Ешкім табылмады',
        'Басқа есім немесе Email жазып көріңіз.',
      );
    }

    // Фильтруем тех, кто уже в списке друзей (даже если не подтвержден)
    final friendIds = friends.map((f) => f.id).toSet();
    final discoverable =
        list.where((u) => !friendIds.contains(u['id'])).toList();

    if (discoverable.isEmpty && _searchCtrl.text.isEmpty) {
      return _buildEmptyState(
        Icons.check_circle_outline_rounded,
        'Керемет!',
        'Сіз барлық қолжетімді қолданушыларды қосып қойғансыз.',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: discoverable.length,
      itemBuilder: (ctx, i) {
        final u = discoverable[i];
        return _DiscoverUserTile(
          user: u,
          isDark: isDark,
          onAdd: () => _addOrConfirm(
              u['id'],
              '${u['first_name'] ?? ''} ${u['last_name'] ?? ''}'.trim().isEmpty
                  ? u['email']
                  : '${u['first_name'] ?? ''} ${u['last_name'] ?? ''}'.trim()),
        );
      },
    );
  }

  Widget _buildEmptyState(IconData icon, String title, String subtitle) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: const Color(0xFF4C45E5).withValues(alpha: 0.08),
                shape: BoxShape.circle,
              ),
              child: Icon(icon,
                  size: 64, color: const Color(0xFF4C45E5).withValues(alpha: 0.5)),
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              subtitle,
              style: TextStyle(
                  fontSize: 14, color: Colors.grey.shade600, height: 1.5),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 12, top: 4),
      child: Text(
        title,
        style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.2,
            color: Colors.grey.shade500),
      ),
    );
  }
}

class _FriendTile extends StatelessWidget {
  final Friend friend;
  final bool isDark;
  final bool isPending;

  const _FriendTile(
      {required this.friend, required this.isDark, this.isPending = false});

  @override
  Widget build(BuildContext context) {
    final hasLocation = friend.lat != null && friend.lon != null;
    const primaryColor = Color(0xFF4C45E5);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          )
        ],
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Stack(
          children: [
            CircleAvatar(
              radius: 26,
              backgroundColor: primaryColor.withValues(alpha: 0.1),
              child: Text(
                friend.name.isNotEmpty ? friend.name[0].toUpperCase() : '?',
                style: const TextStyle(
                    color: primaryColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 20),
              ),
            ),
            if (hasLocation)
              Positioned(
                right: 0,
                bottom: 0,
                child: Container(
                  width: 14,
                  height: 14,
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981),
                    shape: BoxShape.circle,
                    border: Border.all(
                        color: isDark ? const Color(0xFF1E293B) : Colors.white,
                        width: 2),
                  ),
                ),
              ),
          ],
        ),
        title: Text(
          friend.name,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Row(
            children: [
              Icon(
                isPending
                    ? Icons.hourglass_top_rounded
                    : (hasLocation
                        ? Icons.location_on_rounded
                        : Icons.location_off_rounded),
                size: 14,
                color: isPending
                    ? Colors.orange
                    : (hasLocation ? const Color(0xFF10B981) : Colors.grey),
              ),
              const SizedBox(width: 4),
              Text(
                isPending
                    ? 'Жауап күтілуде'
                    : (hasLocation ? 'Локация бөлісуде' : 'Офлайн / Жасырын'),
                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
              ),
            ],
          ),
        ),
        trailing: isPending
            ? const Icon(Icons.chevron_right_rounded, color: Colors.grey)
            : (hasLocation
                ? const Icon(Icons.arrow_forward_ios_rounded,
                    size: 14, color: primaryColor)
                : null),
      ),
    );
  }
}

class _UserRequestTile extends StatelessWidget {
  final Map<String, dynamic> user;
  final bool isDark;
  final VoidCallback onConfirm;

  const _UserRequestTile(
      {required this.user, required this.isDark, required this.onConfirm});

  @override
  Widget build(BuildContext context) {
    const primaryColor = Color(0xFF4C45E5);
    final name = user['name'] ?? user['email'] ?? 'Пайдаланушы';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: primaryColor.withValues(alpha: 0.2), width: 1),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: primaryColor.withValues(alpha: 0.1),
            child: const Icon(Icons.person_add_alt_1_rounded,
                color: Color(0xFF4C45E5)),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name,
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 15)),
                Text('Сізді қосқысы келеді',
                    style:
                        TextStyle(fontSize: 12, color: Colors.grey.shade600)),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: onConfirm,
            style: ElevatedButton.styleFrom(
              backgroundColor: primaryColor,
              foregroundColor: Colors.white,
              elevation: 0,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
            child: const Text('ҚАБЫЛДАУ',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

class _DiscoverUserTile extends StatelessWidget {
  final Map<String, dynamic> user;
  final bool isDark;
  final VoidCallback onAdd;

  const _DiscoverUserTile(
      {required this.user, required this.isDark, required this.onAdd});

  @override
  Widget build(BuildContext context) {
    const primaryColor = Color(0xFF4C45E5);
    final f = user['first_name'] ?? '';
    final l = user['last_name'] ?? '';
    final name = '$f $l'.trim().isEmpty ? user['email'] : '$f $l'.trim();

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(20),
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.grey.shade200,
          child: const Icon(Icons.person_outline, color: Colors.grey),
        ),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle:
            Text(user['email'] ?? '', style: const TextStyle(fontSize: 12)),
        trailing: IconButton(
          icon: const Icon(Icons.person_add_rounded, color: primaryColor),
          onPressed: onAdd,
        ),
      ),
    );
  }
}
