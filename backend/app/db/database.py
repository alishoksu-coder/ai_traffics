# backend/app/db/database.py
import sqlite3
from pathlib import Path
from typing import Generator

from app.config import settings
from app.db.schema import ensure_schema

def _default_db_path() -> str:
    """Возвращает путь к базе по умолчанию."""
    return str(Path(__file__).resolve().parents[2] / "data" / "traffic.db")

def create_conn(db_path: str | None = None) -> sqlite3.Connection:
    """
    Создаёт соединение с БД. Если db_path не указан, берём settings.db_path или дефолт.
    """
    path = db_path or getattr(settings, "db_path", None) or _default_db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)  # создаём таблицы, если их нет
    return conn

# обычная функция для main.py
def get_conn(db_path: str | None = None) -> sqlite3.Connection:
    """Возвращает соединение с БД (не генератор)."""
    return create_conn(db_path)

# генератор для FastAPI Depends
def get_conn_dep() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency."""
    conn = create_conn()
    try:
        yield conn
    finally:
        conn.close()