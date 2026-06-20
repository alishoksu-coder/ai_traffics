# backend/app/services/friends_service.py
"""
Сервис для социальных функций: AI Meet in the Middle.
"""
import numpy as np
from datetime import datetime
from fastapi import HTTPException
import sqlite3

from app.ml.ensemble import traffic_ensemble
from app.repositories.traffic_repository import get_locations


def calculate_smart_meet(conn: sqlite3.Connection, user_locations: list, meeting_time_offset_min: int):
    """
    AI Meet in the Middle: Вычисляет оптимальную точку встречи
    с учетом прогноза пробок от Ансамбля (LSTM + RF) на N минут вперед.
    """
    if not user_locations or len(user_locations) < 2:
        raise HTTPException(status_code=400, detail="Нужно минимум 2 пользователя")

    dt = datetime.now()
    avg_lat = sum(u['lat'] for u in user_locations) / len(user_locations)
    avg_lng = sum(u['lng'] for u in user_locations) / len(user_locations)

    candidates = []
    locations = get_locations(conn)
    for r in locations:
        dist = np.sqrt((r['lat'] - avg_lat)**2 + (r['lon'] - avg_lng)**2)
        candidates.append({
            "id": r['id'],
            "name": r['name'],
            "lat": r['lat'],
            "lng": r['lon'],
            "dist": dist
        })
        
    candidates.sort(key=lambda x: x["dist"])
    top_candidates = candidates[:3]

    best_candidate = None
    best_score = float('inf')

    for c in top_candidates:
        # TODO: Достать актуальный weather_factor
        pred_congestion = traffic_ensemble.predict(
            c["id"], 
            (dt.hour + (meeting_time_offset_min // 60)) % 24, 
            dt.weekday(), 
            1.0
        )
        score = c["dist"] * 5000 + pred_congestion

        if score < best_score:
            best_score = score
            best_candidate = {
                "location_id": c["id"],
                "name": c["name"],
                "lat": c["lat"],
                "lng": c["lng"],
                "predicted_traffic": round(pred_congestion, 1),
                "suggestion": f"Идеальная точка. Прогнозируемая загруженность через {meeting_time_offset_min} мин: {round(pred_congestion, 1)}%"
            }

    return {"optimal_meeting_point": best_candidate}
