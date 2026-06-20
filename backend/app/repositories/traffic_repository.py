# backend/app/repositories/traffic_repository.py
"""
Репозиторий для работы с данными трафика (traffic_values, road_segments, locations).
Инкапсулирует все SQL-запросы, связанные с мониторингом дорожного трафика.
"""
import sqlite3
import time
from typing import Any, Dict, List, Optional


# ---------- helpers ----------

def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    )
    return cur.fetchone() is not None


def _row_to_dict(row: Any) -> Dict:
    if hasattr(row, "keys"):
        return {k: row[k] for k in row.keys()}
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


# ---------- traffic_values ----------

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
    """
    minutes = int(minutes)
    now_ts = int(time.time())
    since = now_ts - minutes * 60

    if grouping == "auto":
        if minutes <= 720:
            grouping = "minute"
        elif minutes <= 10080:
            grouping = "hour"
        else:
            grouping = "day"

    bucket_map = {"minute": 60, "hour": 3600, "day": 86400}
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
            out.append({"id": t[0], "name": t[1], "location_id": t[2], "polyline": t[3]})
        else:
            out.append(dict(d))
    return out


def upsert_road_segment(conn: sqlite3.Connection, segment_id: int, name: str, location_id: int, polyline: str) -> None:
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


# ---------- legacy ----------

def insert_record(conn: sqlite3.Connection, ts, location_id: int, value: float) -> None:
    from datetime import datetime
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


def commit(conn: sqlite3.Connection) -> None:
    conn.commit()
