import time, random, math, json
import sqlite3
import httpx
from app.db.repository import (
    insert_traffic_values,
    get_locations,
    upsert_location,
    upsert_road_segment,
    get_admin_by_login,
    create_admin,
)
from app.auth import hash_for_storage
from app.config import settings

def seed_history_if_empty(conn: sqlite3.Connection, sim, minutes: int = 240) -> None:
    cnt = conn.execute("SELECT COUNT(*) FROM traffic_values").fetchone()[0]
    if cnt > 0:
        return

    points = sim.snapshot(0)
    if not points:
        return

    loc_ids = [int(p["location_id"]) for p in points if "location_id" in p]
    if not loc_ids:
        return

    now = int(time.time())
    now_min = (now // 60) * 60  # важно: чтобы ts были кратны минуте

    rows = []
    for m in range(minutes, 0, -1):
        ts = now_min - m * 60
        minute_of_day = (ts // 60) % (24 * 60)
        base_wave = 50 + 20 * math.sin(2 * math.pi * (minute_of_day / (24 * 60)))

        for lid in loc_ids:
            noise = random.uniform(-8, 8)
            val = max(0.0, min(100.0, base_wave + noise))
            rows.append({"location_id": lid, "ts": ts, "value": val})

    insert_traffic_values(conn, rows)


# Границы Астаны (центр и окрестности)
ASTANA_LAT_MIN, ASTANA_LAT_MAX = 51.08, 51.26
ASTANA_LON_MIN, ASTANA_LON_MAX = 71.32, 71.58

# Маршруты для полинений дорог Астаны (начало и конец): по ним OSRM вернёт реальную геометрию
ASTANA_ROUTES = [
    # Проспекты восток–запад
    ("Проспект Кабанбай батыра", 51.155, 71.42, 51.155, 71.55),
    ("Проспект Республики", 51.169, 71.41, 51.169, 71.56),
    ("Улица Сыганак", 51.125, 71.43, 51.125, 71.54),
    ("Проспект Туран", 51.14, 71.44, 51.14, 71.53),
    # Проспекты север–юг
    ("Проспект Казахстан", 51.10, 71.47, 51.24, 71.47),
    ("Улица Кунаева", 51.12, 71.43, 51.22, 71.43),
    ("Проспект Мангилик Ел", 51.11, 71.42, 51.24, 71.42),
    ("Улица Кенесары", 51.13, 71.45, 51.22, 71.45),
    ("Проспект Абая", 51.14, 71.46, 51.21, 71.46),
    # Диагонали и связки
    ("Связка центр–север", 51.16, 71.45, 51.22, 71.48),
    ("Связка юг–центр", 51.10, 71.44, 51.16, 71.45),
    ("Улица Орынбор", 51.18, 71.40, 51.18, 71.52),
    ("Бульвар Нуржол", 51.15, 71.41, 51.15, 71.55),
    ("Проспект Тауелсиздик", 51.17, 71.43, 51.17, 71.54),
    ("Улица Жумабаева", 51.13, 71.46, 51.20, 71.46),
    ("Шоссе Коргалжин", 51.12, 71.48, 51.20, 71.48),
    ("Улица Егемен Казахстан", 51.19, 71.44, 51.19, 71.52),
    ("Связка запад–восток", 51.165, 71.38, 51.165, 71.56),
    ("Связка север–юг 2", 51.20, 71.44, 51.12, 71.44),
]


def _closest_location_id(conn, locs, lat: float, lon: float) -> int:
    """Ближайшая локация к точке (lat, lon) по квадрату расстояния."""
    if not locs:
        return 1
    best_id = int(locs[0]["id"])
    best_d2 = 1e18
    for loc in locs:
        dlat = float(loc["lat"]) - lat
        dlon = float(loc["lon"]) - lon
        d2 = dlat * dlat + dlon * dlon
        if d2 < best_d2:
            best_d2 = d2
            best_id = int(loc["id"])
    return best_id


def _fetch_osrm_polyline(lon_a: float, lat_a: float, lon_b: float, lat_b: float) -> list:
    """Запрос к OSRM: возвращает список [[lat, lon], ...] или пустой список."""
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{lon_a},{lat_a};{lon_b},{lat_b}"
        "?overview=full&geometries=geojson"
    )
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(url)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        print(f"WARNING: OSRM request failed for {url[:60]}...: {e}")
        return []
    routes = data.get("routes") or []
    if not routes:
        return []
    coords = routes[0].get("geometry", {}).get("coordinates") or []
    # OSRM даёт [lon, lat]; нам [lat, lon]
    return [[float(c[1]), float(c[0])] for c in coords]


def seed_locations_astana_if_empty(conn: sqlite3.Connection) -> None:
    """Заполняет таблицу locations сеткой точек по всей Астане."""
    cnt = conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
    if cnt > 0:
        print(f"DEBUG: Locations already exist: {cnt}")
        return

    n_lat, n_lon = 12, 12
    loc_id = 1
    for i in range(n_lat):
        lat = ASTANA_LAT_MIN + (ASTANA_LAT_MAX - ASTANA_LAT_MIN) * (i / max(1, n_lat - 1))
        for j in range(n_lon):
            lon = ASTANA_LON_MIN + (ASTANA_LON_MAX - ASTANA_LON_MIN) * (j / max(1, n_lon - 1))
            upsert_location(conn, loc_id, f"Астана {loc_id}", lat, lon)
            loc_id += 1
    conn.commit()
    print(f"DEBUG: Created {loc_id - 1} locations for Astana")


def seed_segments_if_empty(conn: sqlite3.Connection) -> None:
    cnt = conn.execute("SELECT COUNT(*) FROM road_segments").fetchone()[0]
    if cnt > 0:
        print(f"DEBUG: Road segments already exist: {cnt}")
        return

    locs = get_locations(conn)
    if not locs:
        print("WARNING: No locations found, cannot create segments")
        return

    seg_id = 1
    created = 0
    # Полинии дорог Астаны: реальная геометрия через OSRM (видны линии и транспорт)
    for name, lat_a, lon_a, lat_b, lon_b in ASTANA_ROUTES:
        poly = _fetch_osrm_polyline(lon_a, lat_a, lon_b, lat_b)
        if len(poly) < 2:
            # Fallback: короткий отрезок между точками, если OSRM не вернул маршрут
            poly = [[lat_a, lon_a], [lat_b, lon_b]]
        location_id = _closest_location_id(conn, locs, lat_a, lon_a)
        upsert_road_segment(
            conn,
            segment_id=seg_id,
            name=name,
            location_id=location_id,
            polyline=json.dumps(poly),
        )
        seg_id += 1
        created += 1
    conn.commit()
    print(f"DEBUG: Created {created} road segments (OSRM polylines for Astana)")


def seed_admin_if_empty(conn: sqlite3.Connection) -> None:
    """Создаёт админа по умолчанию из настроек, если ни одного нет."""
    try:
        cnt = conn.execute("SELECT COUNT(*) FROM admin_users").fetchone()[0]
    except sqlite3.OperationalError:
        return  # таблица ещё не создана
    if cnt > 0:
        return
    if get_admin_by_login(conn, settings.admin_login):
        return
    create_admin(conn, settings.admin_login, hash_for_storage(settings.admin_password))
    conn.commit()
    print(f"DEBUG: Created default admin user: {settings.admin_login}")
