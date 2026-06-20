# backend/app/services/admin_service.py
"""
Сервис для работы с административной панелью: авторизация и сбор статистики.
"""
from fastapi import HTTPException
import sqlite3

from app.core.security import verify_admin_password, create_admin_token, verify_admin_token, hash_for_storage
from app.repositories.user_repository import get_admin_by_login, create_admin, commit
from app.services.simulation_service import sim
from app.vehicles import veh_sim

def authenticate_admin(conn: sqlite3.Connection, login: str, password: str):
    user = get_admin_by_login(conn, login)
    if not user or not verify_admin_password(user.get("password_hash"), password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return create_admin_token(int(user["id"]))

def register_admin(conn: sqlite3.Connection, login: str, password: str):
    user = get_admin_by_login(conn, login)
    if user:
        raise HTTPException(status_code=400, detail="Мұндай логин тіркелген (User already exists)")
    
    hashed = hash_for_storage(password)
    create_admin(conn, login, hashed)
    commit(conn)
    
    user_new = get_admin_by_login(conn, login)
    if not user_new:
        raise HTTPException(status_code=500, detail="Тіркелу қатесі (Registration error)")
    return create_admin_token(int(user_new["id"]))

def get_dashboard_stats(conn: sqlite3.Connection, authorization: str):
    token = (authorization or "").replace("Bearer ", "")
    admin_id = verify_admin_token(token)
    if admin_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        locations_count = conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
    except:
        locations_count = 0
        
    try:
        segments_count = conn.execute("SELECT COUNT(*) FROM road_segments").fetchone()[0]
    except:
        segments_count = 0
        
    try:
        friends_count = conn.execute("SELECT COUNT(*) FROM friends").fetchone()[0]
    except:
        friends_count = 0

    items = sim.snapshot(0)
    avg_val = 0.0
    if items:
        avg_val = sum(it.get('value', 0.0) for it in items) / len(items)

    admin_row = conn.execute("SELECT login FROM admin_users WHERE id = ?", (admin_id,)).fetchone()
    admin_name = admin_row[0] if admin_row else "Админ"

    return {
        "admin_name": admin_name,
        "locations_count": locations_count,
        "segments_count": segments_count,
        "friends_count": friends_count,
        "sim_running": sim.is_running(),
        "hotspots": sim.hotspots_count(),
        "avg_traffic_value": round(avg_val, 1),
        "traffic_score": max(1, round(avg_val / 10.0)) if items else 0,
        "vehicles_count": len(veh_sim.snapshot()),
    }
