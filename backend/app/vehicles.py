# backend/app/vehicles.py — симуляция автобусов и машин вдоль маршрутов
import json
import math
import random
import threading
import time
from typing import Any, Callable, Dict, List

def _interpolate_polyline(points: List[List[float]], progress: float) -> tuple[float, float]:
    """progress 0..1 → (lat, lon) вдоль линии."""
    if not points:
        return 51.16, 71.45
    n = len(points)
    if n == 1:
        return float(points[0][0]), float(points[0][1])
    total = (n - 1) * max(0.01, progress)
    i = int(total) % (n - 1)
    t = total - int(total)
    if i >= n - 1:
        i = n - 2
        t = 1.0
    a, b = points[i], points[i + 1]
    lat = a[0] + (b[0] - a[0]) * t
    lon = a[1] + (b[1] - a[1]) * t
    return float(lat), float(lon)


class VehicleSimulator:
    """Держит список транспорта (автобусы/машины), двигает их вдоль сегментов дорог."""

    def __init__(self, get_segments: Callable[[], List[Dict]]):
        self._get_segments = get_segments
        self._lock = threading.Lock()
        self._vehicles: List[Dict[str, Any]] = []  # {id, type, segment_id, progress, route_name}
        self._next_id = 1
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True
            self._spawn_vehicles()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        with self._lock:
            self._running = False

    def _spawn_vehicles(self) -> None:
        segs = self._get_segments()
        segments_with_points = [s for s in segs if self._point_count(s) >= 2]
        if not segments_with_points:
            return
        self._vehicles.clear()
        self._next_id = 1
        # Автобусы (имитация городского транспорта Астаны)
        for _ in range(14):
            s = random.choice(segments_with_points)
            self._vehicles.append({
                "id": self._next_id,
                "type": "bus",
                "segment_id": int(s.get("id", 0)),
                "progress": random.uniform(0, 1),
                "route_name": str(s.get("name", "")),
            })
            self._next_id += 1
        # Машины
        for _ in range(28):
            s = random.choice(segments_with_points)
            self._vehicles.append({
                "id": self._next_id,
                "type": "car",
                "segment_id": int(s.get("id", 0)),
                "progress": random.uniform(0, 1),
                "route_name": str(s.get("name", "")),
            })
            self._next_id += 1

    def _point_count(self, s: Dict) -> int:
        p = s.get("polyline")
        if isinstance(p, str):
            try:
                return len(json.loads(p))
            except Exception:
                return 0
        return len(p) if isinstance(p, list) else 0

    def _get_polyline(self, segment_id: int) -> List[List[float]]:
        for s in self._get_segments():
            if int(s.get("id", 0)) == segment_id:
                p = s.get("polyline")
                if isinstance(p, str):
                    try:
                        return json.loads(p)
                    except Exception:
                        return []
                return list(p) if isinstance(p, list) else []
        return []

    def _loop(self) -> None:
        while True:
            with self._lock:
                if not self._running:
                    break
                segs = self._get_segments()
                seg_by_id = {int(s.get("id", 0)): s for s in segs}
                for v in self._vehicles:
                    sid = v["segment_id"]
                    v["progress"] = v["progress"] + random.uniform(0.015, 0.035)
                    if v["progress"] >= 1.0:
                        v["progress"] = 0.0
                        seg_list = [s for s in segs if self._point_count(s) >= 2]
                        if seg_list:
                            s = random.choice(seg_list)
                            v["segment_id"] = int(s.get("id", 0))
                            v["route_name"] = str(s.get("name", ""))
                    s = seg_by_id.get(sid)
                    if s:
                        v["route_name"] = str(s.get("name", ""))
            time.sleep(1.2)

    def snapshot(self) -> List[Dict[str, Any]]:
        """Текущие позиции транспорта: {id, type, lat, lon, route_name}."""
        segs = self._get_segments()
        seg_by_id = {int(s.get("id", 0)): s for s in segs}
        result = []
        with self._lock:
            for v in self._vehicles:
                points = self._get_polyline(v["segment_id"])
                if not points:
                    lat, lon = 51.16, 71.45
                else:
                    lat, lon = _interpolate_polyline(points, v["progress"] % 1.0)
                result.append({
                    "id": v["id"],
                    "type": v["type"],
                    "lat": lat,
                    "lon": lon,
                    "route_name": v.get("route_name", ""),
                })
        return result
