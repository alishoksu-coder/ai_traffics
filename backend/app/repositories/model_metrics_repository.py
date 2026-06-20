# backend/app/repositories/model_metrics_repository.py
"""
Репозиторий для сохранения и получения метрик ML-моделей (MAE, RMSE)
и истории предсказаний.
"""
import sqlite3
import time
from typing import Dict, List


def insert_model_metric(conn: sqlite3.Connection, model_name: str, horizon: int, mae: float, rmse: float, n: int) -> None:
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO model_metrics (model_name, horizon, mae, rmse, n, ts)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (model_name, int(horizon), float(mae), float(rmse), int(n), int(time.time())))


def insert_model_prediction(conn: sqlite3.Connection, model_name: str, segment_id: int, predicted_value: float, horizon_min: int) -> None:
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO model_predictions (model_name, segment_id, predicted_value, horizon_min, predicted_at)
        VALUES (?, ?, ?, ?, ?)
    """, (model_name, int(segment_id), float(predicted_value), int(horizon_min), int(time.time())))


def get_model_status(conn: sqlite3.Connection) -> List[Dict]:
    """Возвращает последние рассчитанные метрики по моделям."""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT model_name, horizon, mae, rmse, n, ts
            FROM model_metrics
            WHERE id IN (
                SELECT MAX(id) FROM model_metrics GROUP BY model_name, horizon
            )
        """)
        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({
                "model_name": r[0],
                "horizon": r[1],
                "mae": r[2],
                "rmse": r[3],
                "n": r[4],
                "ts": r[5]
            })
        return out
    except sqlite3.OperationalError:
        return []

def get_latest_metrics_by_horizon(conn: sqlite3.Connection, horizon: int) -> List[Dict]:
    """Возвращает метрики всех моделей для заданного горизонта прогнозирования."""
    rows = conn.execute("""
        SELECT model_name, horizon, mae, rmse, n, ts
        FROM model_metrics
        WHERE horizon = ?
        AND ts = (SELECT MAX(ts) FROM model_metrics WHERE horizon = ?)
    """, (horizon, horizon)).fetchall()
    
    return [{"model_name": r[0], "horizon": r[1], "mae": r[2], "rmse": r[3], "n": r[4], "ts": r[5]} for r in rows]

def commit(conn: sqlite3.Connection) -> None:
    conn.commit()
