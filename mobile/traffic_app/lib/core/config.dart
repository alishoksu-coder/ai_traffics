// Для тестов на локальном компьютере или телефоне (заменено на облачный Render):
const String kApiBaseUrl = 'https://ai-traffics.onrender.com'; 
// Используем Render, чтобы пользователи могли получить доступ к серверу через интернет.
/// Google Maps API key (Maps SDK + Geocoding API)
const String kGoogleMapsApiKey = 'AIzaSyAl5qz2U_ioqFuxDvZKi5wjwirqMFTr5OA';

/// Вход в «Traffic AI Admin» без `profiles.is_admin` (если в Supabase нельзя выставить флаг).
/// Для продакшена лучше задать `is_admin = true` в таблице `profiles` для нужного пользователя.
const Set<String> kAdminLoginBypassEmails = {
  'alisul123321@gmail.com',
  'slivershow2005@gmail.com',
};
