# backend/app/repositories/user_repository.py
"""
Репозиторий для работы с пользователями: админы, друзья, встречи.
"""
import sqlite3
import time
from typing import Dict, List, Optional


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    )
    return cur.fetchone() is not None


def _row_to_dict(row) -> Dict:
    if hasattr(row, "keys"):
        return {k: row[k] for k in row.keys()}
    return {"_": row}


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
        pass


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
    conn.execute(
        "UPDATE friends SET lat=?, lon=?, updated_at=? WHERE id=?",
        (float(lat), float(lon), int(time.time()), int(friend_id)),
    )


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


def commit(conn: sqlite3.Connection) -> None:
    conn.commit()
