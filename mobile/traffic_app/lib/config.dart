// Для тестов на локальном компьютере или телефоне:
const String kApiBaseUrl = 'http://10.82.155.147:8000'; 
// Используем IP компьютера 10.82.155.147, чтобы телефон его увидел.
/// Google Maps API key (Maps SDK + Geocoding API)
const String kGoogleMapsApiKey = 'AIzaSyAl5qz2U_ioqFuxDvZKi5wjwirqMFTr5OA';

/// Вход в «Traffic AI Admin» без `profiles.is_admin` (если в Supabase нельзя выставить флаг).
/// Для продакшена лучше задать `is_admin = true` в таблице `profiles` для нужного пользователя.
const Set<String> kAdminLoginBypassEmails = {
  'alisul123321@gmail.com',
  'slivershow2005@gmail.com',
};
