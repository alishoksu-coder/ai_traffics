# backend/app/db/repository.py
import sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# ---------- helpers ----------

def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    )
    return cur.fetchone() is not None


def _row_to_dict(row: Any) -> Dict:
    # Works for sqlite3.Row and for tuples (fallback)
    if hasattr(row, "keys"):
        return {k: row[k] for k in row.keys()}
    # if tuple - no column names
    return {"_": row}


# ---------- locations ----------

def upsert_location(conn: sqlite3.Connection, loc_id: int, name: str, lat: float, lon: float) -> None:
    conn.execute(
        """
        INSERT INTO locations(id, name, lat, lon) VALUES(?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            lat=excluded.lat,
            lon=excluded.lon
        """,
        (int(loc_id), str(name), float(lat), float(lon)),
    )


def get_locations(conn: sqlite3.Connection) -> List[Dict]:
    rows = conn.execute("SELECT id, name, lat, lon FROM locations ORDER BY id").fetchall()
    out: List[Dict] = []
    for r in rows:
        d = _row_to_dict(r)
        if "_" in d:
            t = d["_"]
            out.append({"id": t[0], "name": t[1], "lat": t[2], "lon": t[3]})
        else:
            out.append(dict(d))
    return out


def get_location(conn: sqlite3.Connection, loc_id: int) -> Optional[Dict]:
    row = conn.execute(
        "SELECT id, name, lat, lon FROM locations WHERE id = ?",
        (int(loc_id),)
    ).fetchone()
    if row is None:
        return None
    d = _row_to_dict(row)
    if "_" in d:
        t = d["_"]
        return {"id": t[0], "name": t[1], "lat": t[2], "lon": t[3]}
    return dict(d)


# ---------- legacy traffic_records (старое) ----------

def insert_record(conn: sqlite3.Connection, ts: datetime, location_id: int, value: float) -> None:
    ts_str = ts.isoformat() if isinstance(ts, datetime) else str(ts)
    conn.execute(
        "INSERT INTO traffic_records(timestamp, location_id, traffic_value) VALUES(?,?,?)",
        (ts_str, int(location_id), float(value)),
    )


def get_latest_values(conn: sqlite3.Connection) -> List[Dict]:
    if not _table_exists(conn, "traffic_records"):
        return []

    rows = conn.execute(
        """
        SELECT l.id AS location_id, l.lat, l.lon,
               tr.timestamp AS timestamp, tr.traffic_value AS value
        FROM locations l
        JOIN traffic_records tr
          ON tr.location_id = l.id
        WHERE tr.timestamp = (
            SELECT MAX(timestamp) FROM traffic_records WHERE location_id = l.id
        )
        ORDER BY l.id;
        """
    ).fetchall()

    out: List[Dict] = []
    for r in rows:
        d = _row_to_dict(r)
        if "_" in d:
            t = d["_"]
            out.append({"location_id": t[0], "lat": t[1], "lon": t[2], "timestamp": t[3], "value": t[4]})
        else:
            out.append(dict(d))
    return out


# ---------- new traffic_values (для истории/метрик) ----------

def insert_traffic_values(conn: sqlite3.Connection, rows: List[Dict]) -> None:
    if not rows:
        return
    conn.executemany(
        "INSERT INTO traffic_values(location_id, ts, value, weather_factor) VALUES(?,?,?,?)",
        [(int(r["location_id"]), int(r["ts"]), float(r["value"]), float(r.get("weather_factor", 1.0))) for r in rows],
    )
    conn.commit()


def get_history(conn: sqlite3.Connection, minutes: int, grouping: str = "auto") -> List[Dict]:
    """
    Возвращает историю трафика за указанный промежуток.
    grouping: 'minute' | 'hour' | 'day' | 'auto'
      - auto: minute для <=720, hour для <=10080, day для остального
    """
    minutes = int(minutes)
    now_ts = int(time.time())
    since = now_ts - minutes * 60

    # --- Определяем шаг группировки ---
    if grouping == "auto":
        if minutes <= 720:        # до 12 часов — поминутно
            grouping = "minute"
        elif minutes <= 10080:    # до недели — по часам
            grouping = "hour"
        else:                     # месяц и более — по дням
            grouping = "day"

    bucket_map = {
        "minute": 60,
        "hour":   3600,
        "day":    86400,
    }
    bucket = bucket_map.get(grouping, 60)

    if _table_exists(conn, "traffic_values"):
        rows = conn.execute(
            f"""
            SELECT
                location_id,
                (ts / {bucket} * {bucket}) AS b_ts,
                AVG(value)
            FROM traffic_values
            WHERE ts >= ?
            GROUP BY location_id, b_ts
            ORDER BY b_ts ASC
            """,
            (since,),
        ).fetchall()
    elif _table_exists(conn, "traffic_records"):
        # strftime('%s') возвращает строку, нужно кастить к INTEGER для деления
        rows = conn.execute(
            f"""
            SELECT
                location_id,
                (CAST(strftime('%s', timestamp) AS INTEGER) / {bucket} * {bucket}) AS b_ts,
                AVG(traffic_value)
            FROM traffic_records
            WHERE CAST(strftime('%s', timestamp) AS INTEGER) >= ?
            GROUP BY location_id, b_ts
            ORDER BY b_ts ASC
            """,
            (since,),
        ).fetchall()
    else:
        return []

    out: List[Dict] = []
    for r in rows:
        try:
            # Безопасное извлечение по индексам (Row или tuple)
            lid = r[0]
            ts_val = r[1]
            avg_val = r[2] if r[2] is not None else 0.0
            out.append({
                "location_id": int(lid),
                "ts": int(ts_val),
                "value": float(avg_val)
            })
        except (TypeError, ValueError, IndexError) as e:
            print(f"History parse error: {e}")
            continue
    return out


def get_last_value_per_location(conn: sqlite3.Connection) -> Dict[int, Dict]:
    if _table_exists(conn, "traffic_values"):
        rows = conn.execute(
            """
            SELECT tv.location_id, tv.ts, tv.value
            FROM traffic_values tv
            JOIN (
                SELECT location_id, MAX(ts) AS mx
                FROM traffic_values
                GROUP BY location_id
            ) t
            ON t.location_id = tv.location_id AND t.mx = tv.ts
            """
        ).fetchall()
    elif _table_exists(conn, "traffic_records"):
        rows = conn.execute(
            """
            SELECT tr.location_id,
                   CAST(strftime('%s', tr.timestamp) AS INTEGER) AS ts,
                   tr.traffic_value AS value
            FROM traffic_records tr
            JOIN (
                SELECT location_id, MAX(timestamp) AS mx
                FROM traffic_records
                GROUP BY location_id
            ) t
            ON t.location_id = tr.location_id AND t.mx = tr.timestamp
            """
        ).fetchall()
    else:
        return {}

    out: Dict[int, Dict] = {}
    for r in rows:
        d = _row_to_dict(r)
        if "_" in d:
            lid, ts, val = d["_"]
        else:
            lid, ts, val = d["location_id"], d["ts"], d["value"]
        out[int(lid)] = {"ts": int(ts), "value": float(val)}
    return out


# ---------- road_segments ----------

def get_road_segments(conn: sqlite3.Connection, location_id: int | None = None) -> List[Dict]:
    if location_id is not None:
        rows = conn.execute(
            "SELECT id, name, location_id, polyline FROM road_segments WHERE location_id = ? ORDER BY id",
            (int(location_id),)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, name, location_id, polyline FROM road_segments ORDER BY id"
        ).fetchall()

    out: List[Dict] = []
    for r in rows:
        d = _row_to_dict(r)
        if "_" in d:
            t = d["_"]
            out.append({
                "id": t[0],
                "name": t[1],
                "location_id": t[2],
                "polyline": t[3]
            })
        else:
            out.append(dict(d))
    return out


def upsert_road_segment(conn: sqlite3.Connection, segment_id: int, name: str, location_id: int, polyline: str) -> None:
    """
    Вставка или обновление сегмента дороги.
    polyline — строка JSON вида [[lat, lon], ...]
    """
    conn.execute(
        """
        INSERT INTO road_segments(id, name, location_id, polyline) VALUES(?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            location_id=excluded.location_id,
            polyline=excluded.polyline
        """,
        (int(segment_id), str(name), int(location_id), str(polyline))
    )


# ---------- commit ----------

def commit(conn: sqlite3.Connection) -> None:
    conn.commit()


# ---------- friends ----------

def get_friends(conn: sqlite3.Connection) -> List[Dict]:
    if not _table_exists(conn, "friends"):
        return []
    rows = conn.execute(
        "SELECT id, name, lat, lon, updated_at FROM friends ORDER BY name"
    ).fetchall()
    out: List[Dict] = []
    for r in rows:
        d = _row_to_dict(r)
        if "_" in d:
            t = d["_"]
            out.append({
                "id": t[0],
                "name": t[1],
                "lat": float(t[2]) if t[2] is not None else None,
                "lon": float(t[3]) if t[3] is not None else None,
                "updated_at": int(t[4]) if t[4] is not None else None,
            })
        else:
            row = dict(d)
            if row.get("lat") is not None:
                row["lat"] = float(row["lat"])
            if row.get("lon") is not None:
                row["lon"] = float(row["lon"])
            if row.get("updated_at") is not None:
                row["updated_at"] = int(row["updated_at"])
            out.append(row)
    return out


def add_friend(conn: sqlite3.Connection, name: str) -> int:
    conn.execute(
        "INSERT INTO friends(name, lat, lon, updated_at) VALUES(?, NULL, NULL, NULL)",
        (name.strip(),),
    )
    return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])


def update_friend_location(conn: sqlite3.Connection, friend_id: int, lat: float, lon: float) -> None:
    import time
    conn.execute(
        "UPDATE friends SET lat=?, lon=?, updated_at=? WHERE id=?",
        (float(lat), float(lon), int(time.time()), int(friend_id)),
    )


# ---------- admin_users ----------

def get_admin_by_login(conn: sqlite3.Connection, login: str) -> Optional[Dict]:
    if not _table_exists(conn, "admin_users"):
        return None
    row = conn.execute(
        "SELECT id, login, password_hash FROM admin_users WHERE login = ?",
        (login.strip(),),
    ).fetchone()
    if row is None:
        return None
    d = _row_to_dict(row)
    if "_" in d:
        t = d["_"]
        return {"id": t[0], "login": t[1], "password_hash": t[2]}
    return dict(d)


def create_admin(conn: sqlite3.Connection, login: str, password_hash: str) -> None:
    try:
        conn.execute(
            "INSERT INTO admin_users(login, password_hash) VALUES(?, ?)",
            (login.strip(), password_hash),
        )
    except sqlite3.IntegrityError:
        pass  # login already exists


# ---------- meetings ----------

def create_meeting(conn: sqlite3.Connection, user_id: str, friend_id: str, location_id: int, meeting_time: str) -> int:
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO meetings (user_id, friend_id, location_id, meeting_time)
        VALUES (?, ?, ?, ?)
    """, (user_id, friend_id, int(location_id), meeting_time))
    return int(cur.lastrowid)


def get_user_meetings(conn: sqlite3.Connection, user_id: str) -> List[Dict]:
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.user_id, m.friend_id, m.location_id, m.meeting_time, m.status, l.name as loc_name
        FROM meetings m
        JOIN locations l ON m.location_id = l.id
        WHERE m.user_id = ? OR m.friend_id = ?
        ORDER BY m.meeting_time ASC
    """, (user_id, user_id))
    rows = cur.fetchall()
    
    out: List[Dict] = []
    for r in rows:
        out.append({
            "id": r[0],
            "user_id": r[1],
            "friend_id": r[2],
            "location_id": r[3],
            "meeting_time": r[4],
            "status": r[5],
            "location_name": r[6]
        })
    return out