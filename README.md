AI Traffic Fullstack (Backend + Flutter Mobile)

Backend (Windows, Python 3.10):
1) cd backend
2) py -3.10 -m venv .venv
3) .\.venv\Scripts\Activate.ps1
4) pip install -r requirements.txt
5) uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

При первом запуске автоматически создаётся сетка локаций и сегментов по всей Астане (144 точки). Чтобы заново заполнить карту «на весь город», удалите backend/data/traffic.db и перезапустите backend.

Mobile (Phone + OpenStreetMap):
1) Install Flutter + Android SDK, enable USB debugging
2) Ensure PC and phone are on the same Wi‑Fi
3) Find PC local IP (Windows: ipconfig -> IPv4 Address)
4) Edit: mobile/traffic_app/lib/config.dart
   baseUrl = "http://<PC_IP>:8000"
5) cd mobile/traffic_app
6) flutter pub get
7) flutter run

Check API:
- http://<PC_IP>:8000/docs
