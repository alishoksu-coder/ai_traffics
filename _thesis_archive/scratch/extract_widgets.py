import os

lib_dir = r'c:\Users\user\Downloads\ai_traffic_fullstack\mobile\traffic_app\lib'
nav_path = os.path.join(lib_dir, 'ui', 'screens', 'navigator', 'navigator_screen.dart')

with open(nav_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('Future<PlaceResult?> _showAddShortcutBottomSheet(String type, String label) async {')
end_idx = content.find('Widget _buildPremiumTextField(', start_idx)

bottom_sheet_code = content[start_idx:end_idx]

bs_file = os.path.join(lib_dir, 'ui', 'widgets', 'add_shortcut_bottom_sheet.dart')
with open(bs_file, 'w', encoding='utf-8') as f:
    f.write('''import 'package:flutter/material.dart';
import '../../services/google_maps_service.dart';
import 'premium_text_field.dart';

''' + bottom_sheet_code.replace('_buildPremiumTextField', 'buildPremiumTextField'))

start_pf = content.find('Widget _buildPremiumTextField(')
end_pf = content.find('void _updateMapStyle() {')

pf_code = content[start_pf:end_pf]
pf_file = os.path.join(lib_dir, 'ui', 'widgets', 'premium_text_field.dart')
with open(pf_file, 'w', encoding='utf-8') as f:
    f.write('''import 'package:flutter/material.dart';

''' + pf_code.replace('_buildPremiumTextField', 'buildPremiumTextField'))

new_content = content[:start_idx] + content[end_pf:]
new_content = new_content.replace('_showAddShortcutBottomSheet', 'showAddShortcutBottomSheet(context, ')

imports = """import '../../widgets/add_shortcut_bottom_sheet.dart';
import '../../widgets/premium_text_field.dart';
"""
new_content = new_content.replace("import '../../../services/api_client.dart';", "import '../../../services/api_client.dart';\n" + imports)

with open(nav_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Fix signature
bs_content = open(bs_file, 'r', encoding='utf-8').read()
bs_content = bs_content.replace('Future<PlaceResult?> _showAddShortcutBottomSheet(String type, String label)', 'Future<PlaceResult?> showAddShortcutBottomSheet(BuildContext context, String type, String label)')
open(bs_file, 'w', encoding='utf-8').write(bs_content)

pf_content = open(pf_file, 'r', encoding='utf-8').read()
pf_content = pf_content.replace('Widget buildPremiumTextField(', 'Widget buildPremiumTextField(BuildContext context, ')
open(pf_file, 'w', encoding='utf-8').write(pf_content)

print("Widgets extracted")
