import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:traffic_app/app.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    // ВСТАВЬТЕ СЮДА ВАШИ ДАННЫЕ ИЗ SUPABASE:
    url: 'https://nxmefixitnmfzgaxlzsl.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im54bWVmaXhpdG5tZnpnYXhsenNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NjIzNzYsImV4cCI6MjA4OTQzODM3Nn0.g-fY2uUmraHS-Vs9zLcoF1mPuwnhlZzHPlrR_cYXOTU', 
  );

  runApp(const TrafficApp());
}
