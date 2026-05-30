import os
import glob

lib_dir = r'c:\Users\user\Downloads\ai_traffic_fullstack\mobile\traffic_app\lib'
old_api = os.path.join(lib_dir, 'services', 'api.dart')
if os.path.exists(old_api):
    os.remove(old_api)

all_dart_files = glob.glob(os.path.join(lib_dir, '**', '*.dart'), recursive=True)

for file_path in all_dart_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'services/api.dart' in content:
        content = content.replace('services/api.dart', 'services/api_client.dart')
        content = content.replace("import 'api_client.dart';", "import 'api_client.dart';\nimport 'google_maps_service.dart';")
        content = content.replace("import '../services/api_client.dart';", "import '../services/api_client.dart';\nimport '../services/google_maps_service.dart';")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Imports fixed.")
