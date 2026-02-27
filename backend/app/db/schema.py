# backend/app/db/schema.py
import sqlite3

def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id   INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        lat  REAL NOT NULL,
        lon  REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS traffic_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        ts INTEGER NOT NULL,
        value REAL NOT NULL
    );
    """)

    # 1 точка в минуту на локацию
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS ux_tv_loc_ts
    ON traffic_values(location_id, ts);
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_tv_ts ON traffic_values(ts);")

    # сегменты дорог (polyline хранится как JSON-строка [[lat,lon],...])
    cur.execute("""
    CREATE TABLE IF NOT EXISTS road_segments (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        location_id INTEGER NOT NULL,
        polyline TEXT NOT NULL
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_rs_loc ON road_segments(location_id);")

    # Друзья: список с именами и опциональной геолокацией (как реальные друзья)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        lat REAL,
        lon REAL,
        updated_at INTEGER
    );
    """)

    # Админы: логин/пароль для админ-панели
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    """)

    conn.commit()
