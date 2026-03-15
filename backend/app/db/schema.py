# backend/app/db/schema.py
import sqlite3

def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # locations (чтобы симулятор не падал, если таблицы нет)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id   INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        lat  REAL NOT NULL,
        lon  REAL NOT NULL
    );
    """)

    # История значений трафика
    cur.execute("""
    CREATE TABLE IF NOT EXISTS traffic_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        ts INTEGER NOT NULL,     -- Unix time (seconds)
        value REAL NOT NULL
    );
    """)

    # Индексы
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tv_loc_ts ON traffic_values(location_id, ts);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tv_ts ON traffic_values(ts);")

    # Сегменты дорог
    cur.execute("""
    CREATE TABLE IF NOT EXISTS road_segments (
        id          INTEGER PRIMARY KEY,
        name        TEXT NOT NULL DEFAULT '',
        location_id INTEGER NOT NULL,
        polyline    TEXT NOT NULL DEFAULT '[]'
    );
    """)

    # Друзья
    cur.execute("""
    CREATE TABLE IF NOT EXISTS friends (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        lat        REAL,
        lon        REAL,
        updated_at INTEGER
    );
    """)

    # Админы
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        login         TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
    """)

    conn.commit()
