# backend/app/main.py
import os
import time
import threading
import json
import math
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, Query, Body, HTTPException, Depends, Header

from app.config import settings
from app.db.database import get_conn
from app.db.schema import ensure_schema
from app.db.repository import (
    get_locations,
    get_location,
    get_history,
    insert_traffic_values,
    get_road_segments,
    upsert_road_segment,
    get_friends,
    add_friend,
    update_friend_location,
    get_admin_by_login,
    create_admin,
)
from app.simulate import TrafficSimulator
from app.seed import (
    seed_history_if_empty,
    seed_locations_astana_if_empty,
    seed_segments_if_empty,
    seed_admin_if_empty,
)
from app.auth import verify_admin_password, create_admin_token, verify_admin_token, hash_for_storage
from app.vehicles import VehicleSimulator

from app.predict import (
    group_by_location,
    predict_naive,
    predict_moving_avg,
    predict_trend_lr,
    mae_rmse,
)

sim = TrafficSimulator(settings.db_path, tick_seconds=2.0)


def _get_segments_for_vehicles():
    """Список сегментов с polyline как list для симулятора транспорта."""
    conn = get_conn(settings.db_path)
    try:
        segs = get_road_segments(conn)
        out = []
        for s in segs:
            poly = s.get("polyline")
            if isinstance(poly, str):
                try:
                    poly = json.loads(poly)
                except Exception:
                    poly = []
            out.append({"id": s.get("id"), "name": s.get("name", ""), "polyline": poly or []})
        return out
    finally:
        conn.close()


vehicle_sim = VehicleSimulator(get_segments=_get_segments_for_vehicles)

_writer_stop = threading.Event()
_writer_thread: threading.Thread | None = None


def _history_writer_loop():
    last_min_ts = None
    while not _writer_stop.is_set():
        try:
            now = int(time.time())
            min_ts = (now // 60) * 60

            if last_min_ts != min_ts:
                snap = sim.snapshot(0)
                rows = [
                    {"location_id": int(p["location_id"]), "ts": min_ts, "value": float(p["value"])}
                    for p in snap
                    if "location_id" in p and "value" in p
                ]
                if rows:
                    conn = get_conn(settings.db_path)
                    try:
                        insert_traffic_values(conn, rows)
                    finally:
                        conn.close()
                last_min_ts = min_ts

        except Exception:
            pass

        sleep_s = 60 - (int(time.time()) % 60)
        _writer_stop.wait(float(max(1, sleep_s)))


def _next_segment_id() -> int:
    conn = get_conn(settings.db_path)
    try:
        row = conn.execute("SELECT COALESCE(MAX(id),0) + 1 FROM road_segments").fetchone()
        return int(row[0]) if row else 1
    finally:
        conn.close()


def _closest_location_id(lat: float, lon: float) -> int:
    conn = get_conn(settings.db_path)
    locs = []
    try:
        locs = get_locations(conn)
    finally:
        conn.close()

    if not locs:
        raise HTTPException(status_code=400, detail="no locations in DB")

    def haversine_m(lat1, lon1, lat2, lon2):
        R = 6371000.0
        p1 = math.radians(lat1)
        p2 = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
        return 2 * R * math.asin(math.sqrt(a))

    best_id = int(locs[0]["id"])
    best_d = 10**18
    for l in locs:
        d = haversine_m(lat, lon, float(l["lat"]), float(l["lon"]))
        if d < best_d:
            best_d = d
            best_id = int(l["id"])
    return best_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_conn(settings.db_path)
    try:
        ensure_schema(conn)
        seed_locations_astana_if_empty(conn)
        seed_segments_if_empty(conn)
        seed_admin_if_empty(conn)
    finally:
        conn.close()

    sim.start()
    vehicle_sim.start()

    conn = get_conn(settings.db_path)
    try:
        seed_history_if_empty(conn, sim, minutes=240)
    finally:
        conn.close()

    global _writer_thread
    _writer_stop.clear()
    _writer_thread = threading.Thread(target=_history_writer_loop, daemon=True)
    _writer_thread.start()

    try:
        yield
    finally:
        _writer_stop.set()
        vehicle_sim.stop()
        sim.stop()


app = FastAPI(title="AI Traffic Monitor API", version="0.1", lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "cwd": os.getcwd(),
        "status": "ok",
        "sim_running": sim.is_running(),
        "hotspots": sim.hotspots_count(),
    }


@app.get("/locations")
def locations():
    conn = get_conn(settings.db_path)
    try:
        return {"items": get_locations(conn)}
    finally:
        conn.close()


@app.get("/traffic/map")
def traffic_map(horizon: int = Query(0, ge=0, le=60)):
    if horizon not in (0, 30, 60):
        return {"error": "horizon must be 0, 30, or 60"}
    return {"items": sim.snapshot(horizon)}


@app.get("/traffic/history")
def traffic_history(minutes: int = Query(60, ge=5, le=720)):
    conn = get_conn(settings.db_path)
    try:
        return {"items": get_history(conn, minutes)}
    finally:
        conn.close()


@app.post("/roads/segment_from_osrm")
async def segment_from_osrm(payload: dict = Body(...)):
    """
    2 режима:

    A) По location_id (как у тебя сейчас):
      {"id":1(optional), "name":"s1", "a_location_id":7, "b_location_id":17, "probe_location_id":7(optional)}

    B) По координатам (для “тап A/B”):
      {"id":1(optional), "name":"tap_seg", "a":[lat,lon], "b":[lat,lon], "probe_location_id":12(optional)}
    """
    seg_id = int(payload["id"]) if "id" in payload else _next_segment_id()
    name = str(payload.get("name", f"seg{seg_id}"))

    # --- берём A/B ---
    if "a_location_id" in payload and "b_location_id" in payload:
        a_id = int(payload["a_location_id"])
        b_id = int(payload["b_location_id"])
        probe_id = int(payload.get("probe_location_id", a_id))

        conn = get_conn(settings.db_path)
        try:
            a = get_location(conn, a_id)
            b = get_location(conn, b_id)
        finally:
            conn.close()

        if a is None or b is None:
            raise HTTPException(status_code=400, detail=f"location not found: a={a_id}, b={b_id}")

        a_lat, a_lon = float(a["lat"]), float(a["lon"])
        b_lat, b_lon = float(b["lat"]), float(b["lon"])

    else:
        a = payload.get("a")
        b = payload.get("b")
        if not a or not b or len(a) != 2 or len(b) != 2:
            raise HTTPException(status_code=400, detail="provide a/b or a_location_id/b_location_id")

        a_lat, a_lon = float(a[0]), float(a[1])
        b_lat, b_lon = float(b[0]), float(b[1])

        # чтобы сегмент получил value/цвет — привязываем к ближайшей локации к точке A
        probe_id = int(payload.get("probe_location_id") or _closest_location_id(a_lat, a_lon))

    # --- OSRM route ---
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{a_lon},{a_lat};{b_lon},{b_lat}"
        "?overview=full&geometries=geojson"
    )

    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    routes = data.get("routes") or []
    if not routes:
        raise HTTPException(status_code=400, detail="no route from osrm")

    coords = routes[0]["geometry"]["coordinates"]  # [[lon, lat], ...]
    polyline = [[float(lat), float(lon)] for lon, lat in coords]  # [[lat, lon], ...]

    # --- save ---
    conn = get_conn(settings.db_path)
    try:
        upsert_road_segment(conn, seg_id, name, probe_id, polyline)
    finally:
        conn.close()

    return {"ok": True, "id": seg_id, "points_count": len(polyline), "probe_location_id": probe_id}


@app.get("/roads/segments")
def roads_segments(horizon: int = Query(0, ge=0, le=60)):
    if horizon not in (0, 30, 60):
        return {"error": "horizon must be 0, 30, or 60"}

    snap = sim.snapshot(horizon)
    val_by_loc = {
        int(p["location_id"]): float(p["value"])
        for p in snap
        if "location_id" in p and "value" in p
    }

    conn = get_conn(settings.db_path)
    try:
        segs = get_road_segments(conn)
        items = []
        for s in segs:
            try:
                poly_str = s["polyline"]
                if isinstance(poly_str, str):
                    poly = json.loads(poly_str)
                else:
                    poly = poly_str if isinstance(poly_str, list) else []
            except Exception as e:
                print(f"WARNING: Failed to parse polyline for segment {s.get('id')}: {e}")
                poly = []

            loc_id = int(s["location_id"])
            loc = get_location(conn, loc_id)
            location_name = loc.get("name", "") if loc else ""
            if len(poly) >= 2:  # только сегменты с минимум 2 точками
                items.append(
                    {
                        "id": int(s["id"]),
                        "name": s["name"],
                        "location_id": loc_id,
                        "location_name": location_name,
                        "polyline": poly,
                        "value": val_by_loc.get(loc_id, None),
                    }
                )
        print(f"DEBUG: Returning {len(items)} segments for horizon={horizon}")
        return {"horizon": horizon, "items": items}
    finally:
        conn.close()


@app.get("/vehicles")
def get_vehicles():
    """Транспорт на карте: автобусы и машины вдоль маршрутов."""
    return {"items": vehicle_sim.snapshot()}


# ---------- Друзья (как реальные друзья: список + геолокация) ----------

@app.get("/friends")
def friends_list():
    conn = get_conn(settings.db_path)
    try:
        return {"items": get_friends(conn)}
    finally:
        conn.close()


@app.post("/friends")
def friends_add(payload: dict = Body(...)):
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    conn = get_conn(settings.db_path)
    try:
        fid = add_friend(conn, name)
        conn.commit()
        return {"ok": True, "id": fid, "name": name}
    finally:
        conn.close()


@app.put("/friends/{friend_id}/location")
def friends_update_location(
    friend_id: int,
    payload: dict = Body(...),
):
    lat = payload.get("lat")
    lon = payload.get("lon")
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="lat and lon required")
    conn = get_conn(settings.db_path)
    try:
        update_friend_location(conn, friend_id, float(lat), float(lon))
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


# ---------- Админ-панель (логин/пароль) ----------

def require_admin(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization[7:].strip()
    admin_id = verify_admin_token(token)
    if admin_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return admin_id


@app.post("/admin/login")
def admin_login(payload: dict = Body(...)):
    login = (payload.get("login") or "").strip()
    password = payload.get("password") or ""
    if not login or not password:
        raise HTTPException(status_code=400, detail="login and password required")
    conn = get_conn(settings.db_path)
    try:
        admin = get_admin_by_login(conn, login)
    finally:
        conn.close()
    if not admin or not verify_admin_password(admin.get("password_hash"), password):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    token = create_admin_token(int(admin["id"]))
    return {"ok": True, "token": token, "login": login}


@app.get("/admin/dashboard")
def admin_dashboard(admin_id: int = Depends(require_admin)):
    conn = get_conn(settings.db_path)
    try:
        locs = get_locations(conn)
        segs = get_road_segments(conn)
        friends = get_friends(conn)
    finally:
        conn.close()
    return {
        "locations_count": len(locs),
        "segments_count": len(segs),
        "friends_count": len(friends),
        "sim_running": sim.is_running(),
        "hotspots": sim.hotspots_count(),
    }


@app.get("/traffic/metrics")
def traffic_metrics(
    horizon: int = Query(30, ge=0, le=60),
    minutes: int = Query(120, ge=30, le=720),
):
    if horizon not in (0, 30, 60):
        return {"error": "horizon must be 0, 30, or 60"}
    if horizon == 0:
        return {"error": "metrics make sense for horizon=30/60"}

    conn = get_conn(settings.db_path)
    try:
        hist = get_history(conn, minutes)
    finally:
        conn.close()

    by_loc = group_by_location(hist)

    y_true_all = {"naive": [], "ma": [], "trend": []}
    y_pred_all = {"naive": [], "ma": [], "trend": []}

    for _, series in by_loc.items():
        ts_to_val = {ts: v for ts, v in series}
        ts_list = [ts for ts, _ in series]

        for t in ts_list:
            target_t = t + horizon * 60
            if target_t not in ts_to_val:
                continue

            past = [(ts, ts_to_val[ts]) for ts in ts_list if ts <= t]
            if len(past) < 3:
                continue

            true_v = ts_to_val[target_t]

            pred1 = predict_naive(past)
            pred2 = predict_moving_avg(past, k=5)
            pred3 = predict_trend_lr(past, k=10, horizon_min=horizon)

            y_true_all["naive"].append(true_v)
            y_pred_all["naive"].append(pred1)

            y_true_all["ma"].append(true_v)
            y_pred_all["ma"].append(pred2)

            y_true_all["trend"].append(true_v)
            y_pred_all["trend"].append(pred3)

    return {
        "horizon": horizon,
        "minutes_used": minutes,
        "naive": mae_rmse(y_true_all["naive"], y_pred_all["naive"]),
        "moving_avg": mae_rmse(y_true_all["ma"], y_pred_all["ma"]),
        "trend_lr": mae_rmse(y_true_all["trend"], y_pred_all["trend"]),
    }
