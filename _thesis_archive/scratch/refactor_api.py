import os
import shutil
import glob

lib_dir = r'c:\Users\user\Downloads\ai_traffic_fullstack\mobile\traffic_app\lib'

# 1. Move files
moves = {
    'config.dart': 'core',
    'common.dart': 'core',
    'map_styles.dart': 'core',
    'theme_notifier.dart': 'core',
    'models.dart': 'models',
    'api.dart': 'services',
}

for f, folder in moves.items():
    src = os.path.join(lib_dir, f)
    dst = os.path.join(lib_dir, folder, f)
    if os.path.exists(src):
        shutil.move(src, dst)

# Move screens
screens = [f for f in os.listdir(lib_dir) if f.endswith('.dart') and f not in ['main.dart', 'app.dart']]
for s in screens:
    src = os.path.join(lib_dir, s)
    if s == 'navigator_screen.dart':
        dst = os.path.join(lib_dir, 'ui', 'screens', 'navigator', s)
    else:
        dst = os.path.join(lib_dir, 'ui', 'screens', s)
    if os.path.exists(src):
        shutil.move(src, dst)

# 2. Update imports in all files
all_dart_files = glob.glob(os.path.join(lib_dir, '**', '*.dart'), recursive=True)

for file_path in all_dart_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Calculate relative depth to lib/
    rel_path = os.path.relpath(file_path, lib_dir)
    # Number of separators minus 1 (because lib/ is the root, so direct children have 0 depth relative to each other... 
    # Actually if file is in lib/core/config.dart, depth is 1. If we import lib/models/models.dart, we need ../models/models.dart)
    depth = rel_path.count(os.sep)
    prefix = '../' * depth if depth > 0 else ''
    
    # Simple replacements for exact string matches
    replacements = {
        "'api.dart'": f"'{prefix}services/api.dart'",
        "'models.dart'": f"'{prefix}models/models.dart'",
        "'config.dart'": f"'{prefix}core/config.dart'",
        "'common.dart'": f"'{prefix}core/common.dart'",
        "'map_styles.dart'": f"'{prefix}core/map_styles.dart'",
        "'theme_notifier.dart'": f"'{prefix}core/theme_notifier.dart'",
        
        "'splash_screen.dart'": f"'{prefix}ui/screens/splash_screen.dart'",
        "'auth_wrapper.dart'": f"'{prefix}ui/screens/auth_wrapper.dart'",
        "'navigator_screen.dart'": f"'{prefix}ui/screens/navigator/navigator_screen.dart'",
        "'metrics_screen.dart'": f"'{prefix}ui/screens/metrics_screen.dart'",
        "'tips_screen.dart'": f"'{prefix}ui/screens/tips_screen.dart'",
        "'history_screen.dart'": f"'{prefix}ui/screens/history_screen.dart'",
        "'friends_screen.dart'": f"'{prefix}ui/screens/friends_screen.dart'",
        "'more_screen.dart'": f"'{prefix}ui/screens/more_screen.dart'",
        "'drive_screen.dart'": f"'{prefix}ui/screens/drive_screen.dart'",
        "'admin_login_screen.dart'": f"'{prefix}ui/screens/admin_login_screen.dart'",
        "'auth_screen.dart'": f"'{prefix}ui/screens/auth_screen.dart'",
        "'map_screen.dart'": f"'{prefix}ui/screens/map_screen.dart'",
        "'security_settings_screen.dart'": f"'{prefix}ui/screens/security_settings_screen.dart'",
        "'segment_map_page.dart'": f"'{prefix}ui/screens/segment_map_page.dart'",
        "'voice_query_sheet.dart'": f"'{prefix}ui/screens/voice_query_sheet.dart'",
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    # Also replace package imports if any like package:traffic_app/api.dart -> package:traffic_app/services/api.dart
    content = content.replace("'package:traffic_app/api.dart'", "'package:traffic_app/services/api.dart'")
    content = content.replace("'package:traffic_app/models.dart'", "'package:traffic_app/models/models.dart'")
    content = content.replace("'package:traffic_app/common.dart'", "'package:traffic_app/core/common.dart'")
    content = content.replace("'package:traffic_app/theme_notifier.dart'", "'package:traffic_app/core/theme_notifier.dart'")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Files moved and imports updated.")
