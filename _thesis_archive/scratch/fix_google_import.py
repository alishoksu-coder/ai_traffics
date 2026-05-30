import glob

lib_dir = r'c:\Users\user\Downloads\ai_traffic_fullstack\mobile\traffic_app\lib'
all_dart_files = glob.glob(lib_dir + '/**/*.dart', recursive=True)

for file_path in all_dart_files:
    if 'google_maps_service.dart' in file_path:
        continue
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'getPlaceFromQuery' in content or 'PlacePrediction' in content or 'getPlaceDetails' in content or 'getGoogleDirections' in content:
        if 'google_maps_service.dart' not in content:
            content = content.replace("import '../../../services/api_client.dart';", "import '../../../services/api_client.dart';\nimport '../../../services/google_maps_service.dart';")
            content = content.replace("import '../../services/api_client.dart';", "import '../../services/api_client.dart';\nimport '../../services/google_maps_service.dart';")
            content = content.replace("import '../services/api_client.dart';", "import '../services/api_client.dart';\nimport '../services/google_maps_service.dart';")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed {file_path}')
