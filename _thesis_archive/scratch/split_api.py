import os
import re
import glob

api_path = r'c:\Users\user\Downloads\ai_traffic_fullstack\mobile\traffic_app\lib\services\api.dart'
lib_dir = r'c:\Users\user\Downloads\ai_traffic_fullstack\mobile\traffic_app\lib'

with open(api_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to split the file.
# We can find `class ApiClient {`
idx = content.find('class ApiClient {')
part_google = content[:idx]
part_api = content[idx:]

# google maps service
google_maps_content = """import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import '../core/config.dart';

""" + part_google[part_google.find('List<LatLng> decodePolyline'):]

with open(os.path.join(lib_dir, 'services', 'google_maps_service.dart'), 'w', encoding='utf-8') as f:
    f.write(google_maps_content)

# For Traffic and Supabase, since the methods are mixed inside ApiClient, we can just split them into two classes.
# To not parse Dart AST in python, let's just create a `TrafficApiService` and `SupabaseService` by copying ApiClient
# and removing the unrelated methods, or simply just keeping `ApiClient` but renamed to `ApiService` and re-exported.
# BUT the goal is to split large files. 

# A pragmatic approach:
# Create supabase_service.dart
# Create traffic_api_service.dart
# We can define lists of methods.

supabase_methods = ['getUserProfile', 'saveUserShortcut', 'getFriends', 'updateMyLocation', 'searchUserByEmail', 'addFriendById', 'getAllUsers', 'searchUsers', 'getFriendRequests', 'getFriendsWithStatus', 'adminRegister', 'adminLogin']
traffic_methods = ['getParkings', 'simulateClosure', 'getVehicles', 'adminDashboard', 'getRoadSegments', 'getMultimodalAnalysis', 'getArPoints', 'getTrafficRecommendation', 'getWeatherData', 'getTrafficMap', 'getTrafficMetrics', 'getPeakHours', 'getModelMetrics', 'getTrafficHistory', 'getMeetings', 'createMeeting', 'getLocations', 'postEvent', 'getEvents', 'getSmartAlert']

# Actually, adminDashboard mixes both. getTrafficMetrics mixes both.
# It is simpler to keep them in one `ApiService` if they mix, but we can just split `api.dart` into `api_client.dart` and `google_maps_service.dart` 
# That alone splits 500 lines out! 
# And then we can split models? Models are already split.

# Let's just create a single `api_service.dart` for now that holds `ApiClient` and `google_maps_service.dart`.
# Wait, user explicitly asked to split `api.dart` into `google_maps_service.dart`, `traffic_api_service.dart`, `supabase_service.dart`.
# I should do it properly.

