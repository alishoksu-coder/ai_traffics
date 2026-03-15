import math
import random
import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.db.database import get_conn
from app.db.repository import get_locations, insert_traffic_values


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class TrafficSimulator:
    """
    Симулятор "живых" данных:
    - Локации берем из БД (таблица locations).
    - value меняется со временем + иногда создаются "пробки" (hotspots).
    - В ответе добавляем небольшой джиттер lat/lon, чтобы точки "двигались".
    """

    def __init__(self, db_path: str, tick_seconds: float = 2.0):
        self.db_path = db_path
        self.tick_seconds = float(tick_seconds)

        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._running: bool = False

        self._locations: List[Dict] = []
        self._state: Dict[int, Dict] = {}   # id -> {value, base, phase}
        self._hotspots: List[Dict] = []     # {lat, lon, strength, radius_deg, ttl}

        # ✅ чтобы писать в БД не каждый тик, а 1 раз в минуту
        self._last_store_minute: int = -1

        # Погодный фактор (влияет на шум и силу пробок)
        self._weather_factor: float = 1.0

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True

        self._load_locations()
        self._init_state()

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        with self._lock:
            self._running = False

    def is_running(self) -> bool:
        with self._lock:
            return self._running

    def hotspots_count(self) -> int:
        with self._lock:
            return len(self._hotspots)

    def snapshot(self, horizon: int) -> List[Dict]:
        now = time.time()
        iso = datetime.now(timezone.utc).isoformat()

        factor = horizon / 60.0  # 0..1
        result: List[Dict] = []

        with self._lock:
            for loc in self._locations:
                lid = int(loc["id"])
                st = self._state.get(lid)
                if st is None:
                    continue

                cur = float(st["value"])

                # простейший "прогноз": тренд + шум
                trend = (cur - 50.0) * 0.10
                pred = cur + trend * factor * 2.0 + random.uniform(-4.0, 4.0) * (0.3 + factor)
                pred = clamp(pred, 0.0, 100.0)

                # визуальное движение точки
                base_lat = float(loc["lat"])
                base_lon = float(loc["lon"])
                amp = 0.00025  # ~ 20–30 метров
                lat = base_lat + math.sin(now * 0.6 + float(st["phase"])) * amp
                lon = base_lon + math.cos(now * 0.6 + float(st["phase"])) * amp

                result.append({
                    "location_id": lid,
                    "lat": lat,
                    "lon": lon,
                    "value": float(pred),
                    "points": int(round(pred / 10.0)), # 0-10 scale
                    "timestamp": iso,
                    "horizon": horizon,
                })

        return result

    def set_weather_factor(self, factor: float) -> None:
        with self._lock:
            self._weather_factor = float(factor)

    def get_weather_factor(self) -> float:
        with self._lock:
            return self._weather_factor

    def _load_locations(self) -> None:
        conn = get_conn(self.db_path)
        try:
            self._locations = get_locations(conn)
        finally:
            conn.close()

    def _init_state(self) -> None:
        with self._lock:
            self._state.clear()
            for loc in self._locations:
                lid = int(loc["id"])
                base = random.uniform(20.0, 70.0)
                self._state[lid] = {
                    "value": base,
                    "base": base,
                    "phase": random.uniform(0.0, 10.0),
                }

    def _loop(self) -> None:
        next_hotspot_at = time.time() + 5.0

        while True:
            with self._lock:
                if not self._running:
                    break

            t = time.time()
            if t >= next_hotspot_at:
                self._spawn_hotspot()
                next_hotspot_at = t + random.uniform(8.0, 15.0)

            self._tick()
            time.sleep(self.tick_seconds)

    def _spawn_hotspot(self) -> None:
        if not self._locations:
            return

        loc = random.choice(self._locations)
        lat = float(loc["lat"])
        lon = float(loc["lon"])

        hotspot = {
            "lat": lat,
            "lon": lon,
            "strength": random.uniform(20.0, 45.0),
            "radius_deg": 0.01,
            "ttl": time.time() + random.uniform(20.0, 40.0),
        }

        with self._lock:
            self._hotspots.append(hotspot)

    def _tick(self) -> None:
        now = time.time()
        rows_to_store: Optional[List[Dict]] = None

        with self._lock:
            # чистим истёкшие пробки
            self._hotspots = [h for h in self._hotspots if float(h["ttl"]) > now]

            # обновляем value для всех локаций
            for loc in self._locations:
                lid = int(loc["id"])
                st = self._state.get(lid)
                if st is None:
                    continue

                base = float(st["base"])
                wave = math.sin(now * 0.15 + float(st["phase"])) * 8.0
                noise = random.uniform(-3.0, 3.0)

                jam = 0.0
                lat = float(loc["lat"])
                lon = float(loc["lon"])

                wf = self._weather_factor

                for h in self._hotspots:
                    d = math.hypot(lat - float(h["lat"]), lon - float(h["lon"]))
                    radius = float(h["radius_deg"])
                    if d < radius:
                        # Погода усиливает эффект пробки
                        jam += (1.0 - d / radius) * float(h["strength"]) * wf

                # Погода также увеличивает базовый шум
                st["value"] = clamp(base + wave + noise * wf + jam, 0.0, 100.0)

            # ✅ --- store aggregated values once per minute ---
            current_minute = int(now // 60)
            if current_minute != self._last_store_minute:
                self._last_store_minute = current_minute

                ts = int(now)
                rows = []
                for loc in self._locations:
                    lid = int(loc["id"])
                    st = self._state.get(lid)
                    if st is None:
                        continue
                    rows.append({"location_id": lid, "ts": ts, "value": float(st["value"])})

                rows_to_store = rows  # сохраним после выхода из lock

        # ✅ Пишем в БД вне lock (чтобы не тормозить симуляцию)
        if rows_to_store:
            conn = get_conn(self.db_path)
            try:
                insert_traffic_values(conn, rows_to_store)
            except Exception as e:
                # чтобы симулятор не падал из-за БД
                print("TrafficSimulator: store error:", e)
            finally:
                conn.close()
