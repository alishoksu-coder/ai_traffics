import 'package:flutter/material.dart';

import 'api.dart';
import 'models.dart';
import 'common.dart';

class FriendsScreen extends StatefulWidget {
  final VoidCallback? onShowOnMap;

  const FriendsScreen({super.key, this.onShowOnMap});

  @override
  State<FriendsScreen> createState() => _FriendsScreenState();
}

class _FriendsScreenState extends State<FriendsScreen> {
  final api = ApiClient();
  bool loading = true;
  String? error;
  List<Friend> friends = [];

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
      final list = await api.getFriends();
      setState(() {
        friends = list;
        loading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  Future<void> _addFriend() async {
    final name = await showDialog<String>(
      context: context,
      builder: (ctx) {
        final c = TextEditingController();
        return AlertDialog(
          title: const Text('Добавить друга'),
          content: TextField(
            controller: c,
            decoration: const InputDecoration(
              labelText: 'Имя',
              hintText: 'Введите имя',
            ),
            autofocus: true,
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Отмена')),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, c.text.trim()),
              child: const Text('Добавить'),
            ),
          ],
        );
      },
    );
    if (name == null || name.isEmpty) return;
    try {
      await api.addFriend(name);
      _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: whiteAppBar(
        'Друзья',
        actions: [
          if (!loading)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _load,
              tooltip: 'Обновить',
            ),
          if (loading)
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2)),
            ),
        ],
      ),
      body: loading && friends.isEmpty
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : (error != null && friends.isEmpty)
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.error_outline, size: 64, color: Colors.red),
                        const SizedBox(height: 16),
                        Text(error!, textAlign: TextAlign.center),
                        const SizedBox(height: 24),
                        ElevatedButton.icon(
                          onPressed: _load,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Повторить'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    if (widget.onShowOnMap != null && friends.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: SizedBox(
                          width: double.infinity,
                          child: FilledButton.icon(
                            onPressed: () => widget.onShowOnMap?.call(),
                            icon: const Icon(Icons.map),
                            label: const Text('Показать друзей на карте'),
                            style: FilledButton.styleFrom(
                              backgroundColor: AppColors.primary,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                            ),
                          ),
                        ),
                      ),
                    ...friends.map((f) {
                      final hasLocation = f.lat != null && f.lon != null;
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: AppColors.primary.withOpacity(0.2),
                            child: const Icon(Icons.person, color: AppColors.primary),
                          ),
                          title: Text(
                            f.name,
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                          subtitle: hasLocation
                              ? const Text('Местоположение известно', style: TextStyle(fontSize: 12, color: AppColors.textSecondary))
                              : const Text('Местоположение не передано', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                          trailing: hasLocation ? const Icon(Icons.location_on, color: AppColors.primary, size: 20) : null,
                        ),
                      );
                    }),
                  ],
                ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _addFriend,
        icon: const Icon(Icons.person_add),
        label: const Text('Добавить'),
        backgroundColor: AppColors.primary,
      ),
    );
  }
}
