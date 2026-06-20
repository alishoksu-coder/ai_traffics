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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS traffic_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        ts INTEGER NOT NULL,
        value REAL NOT NULL,
        weather_factor REAL DEFAULT 1.0
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

    # Апгрейд для существующей БД: добавляем колонку weather_factor если её нет
    cur.execute("PRAGMA table_info(traffic_values)")
    columns = [col[1] for col in cur.fetchall()]
    if 'weather_factor' not in columns:
        cur.execute("ALTER TABLE traffic_values ADD COLUMN weather_factor REAL DEFAULT 1.0")
        conn.commit()

    # Админы
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        login         TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
    """)

    # Встречи с друзьями
    cur.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT NOT NULL,
        friend_id   TEXT NOT NULL,
        location_id INTEGER NOT NULL,
        meeting_time TEXT NOT NULL,
        status      TEXT DEFAULT 'pending'
    );
    """)

    # Метрики моделей машинного обучения
    cur.execute("""
    CREATE TABLE IF NOT EXISTS model_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        horizon    INTEGER NOT NULL,
        mae        REAL,
        rmse       REAL,
        n          INTEGER,
        ts         INTEGER NOT NULL
    );
    """)

    # Пользовательские события (ДТП, Ремонт, Камера)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type  TEXT NOT NULL,
        lat         REAL NOT NULL,
        lng         REAL NOT NULL,
        created_at  INTEGER NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS model_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        segment_id INTEGER NOT NULL,
        predicted_value REAL NOT NULL,
        actual_value REAL,
        horizon_min INTEGER NOT NULL,
        predicted_at INTEGER NOT NULL,
        verified_at INTEGER
    );
    """)

    cur.execute("""
    INSERT INTO locations (id, name, lat, lon)
    SELECT 1, 'Левый Берег (Байтерек)', 51.1283, 71.4305 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id=1);
    """)
    cur.execute("""
    INSERT INTO locations (id, name, lat, lon)
    SELECT 2, 'Экспо / Mega Silk Way', 51.0903, 71.4182 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id=2);
    """)
    cur.execute("""
    INSERT INTO locations (id, name, lat, lon)
    SELECT 3, 'Хан Шатыр', 51.1325, 71.4038 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id=3);
    """)
    cur.execute("""
    INSERT INTO locations (id, name, lat, lon)
    SELECT 4, 'Проспект Республики', 51.1691, 71.4259 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE id=4);
    """)

    conn.commit()
