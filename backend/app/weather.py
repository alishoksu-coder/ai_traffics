# backend/app/weather.py
import httpx
import time
from typing import Dict, Any

class WeatherService:
    """
    Service to fetch current weather for Astana and determine its impact on traffic.
    """
    def __init__(self, city: str = "Astana"):
        self.city = city
        self._last_weather: Dict[str, Any] = {
            "condition": "clear",
            "temp": 20,
            "traffic_factor": 1.0,
            "description": "Ясно"
        }
        self._last_fetch_ts = 0
        self._cache_ttl = 1800  # 30 minutes

    async def get_current_weather(self) -> Dict[str, Any]:
        now = time.time()
        if now - self._last_fetch_ts < self._cache_ttl:
            return self._last_weather

        try:
            # Using wttr.in as a free, no-key-needed service
            url = f"https://wttr.in/{self.city}?format=j1"
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    data = r.json()
                    current = data['current_condition'][0]
                    temp = int(current['temp_C'])
                    desc = current['lang_ru'][0]['value'] if 'lang_ru' in current else current['weatherDesc'][0]['value']
                    
                    # Determine traffic factor
                    code = int(current['weatherCode'])
                    factor = 1.0
                    cond = "clear"
                    
                    # Very basic mapping of weather codes to traffic factors
                    # Codes: https://www.worldweatheronline.com/feed/wwo-codes.aspx
                    if code in [113, 116]: # Clear, Partly Cloudy
                        factor = 1.0
                        cond = "clear"
                    elif code in [119, 122, 143, 248, 260]: # Cloudy, Overcast, Fog
                        factor = 1.15
                        cond = "cloudy"
                    elif code in [176, 263, 266, 293, 296, 299, 302, 353, 356]: # Light Rain/Drizzle
                        factor = 1.4
                        cond = "rain"
                    elif code in [305, 308, 311, 359]: # Heavy Rain
                        factor = 1.7
                        cond = "rain_heavy"
                    elif code in [179, 182, 185, 227, 230, 323, 326, 329, 332, 335, 338, 368, 371]: # Snow
                        factor = 1.9
                        cond = "snow"
                    elif code in [386, 389, 392, 395]: # Thunderstorm
                        factor = 2.0
                        cond = "storm"

                    self._last_weather = {
                        "condition": cond,
                        "temp": temp,
                        "traffic_factor": factor,
                        "description": desc,
                        "code": code
                    }
                    self._last_fetch_ts = now
        except Exception as e:
            print(f"WeatherService error: {e}")
            # Keep last weather or defaults

        return self._last_weather

weather_service = WeatherService()
