# backend/app/main.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query

from app.config import settings
from app.db.database import get_conn
from app.db.schema import ensure_schema
from app.db.repository import get_locations, get_history
from app.simulate import TrafficSimulator

from app.predict import (
    group_by_location,
    predict_naive,
    predict_moving_avg,
    predict_trend_lr,
    mae_rmse,
    get_trend_analysis,
)
from app.weather import weather_service
import asyncio

sim = TrafficSimulator(settings.db_path, tick_seconds=2.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_conn(settings.db_path)
    try:
        ensure_schema(conn)
    finally:
        conn.close()

    sim.start()
    
    # Background weather update task
    async def update_weather_periodic():
        while True:
            w = await weather_service.get_current_weather()
            sim.set_weather_factor(w['traffic_factor'])
            await asyncio.sleep(600) # update every 10 min

    weather_task = asyncio.create_task(update_weather_periodic())
    
    try:
        yield
    finally:
        weather_task.cancel()
        sim.stop()


app = FastAPI(title="AI Traffic Monitor API", version="0.1", lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "cwd": os.getcwd(),
        "status": "ok",
        "sim_running": sim.is_running(),
        "hotspots": sim.hotspots_count(),
    }


@app.get("/weather")
async def get_weather():
    return await weather_service.get_current_weather()


@app.get("/locations")
def locations():
    conn = get_conn(settings.db_path)
    try:
        return {"items": get_locations(conn)}
    finally:
        conn.close()


@app.get("/weather")
async def weather_api():
    w = await weather_service.get_current_weather()
    return w


@app.get("/traffic/map")
def traffic_map(horizon: int = Query(0, ge=0, le=60)):
    if horizon not in (0, 30, 60):
        return {"error": "horizon must be 0, 30, or 60"}
    items = sim.snapshot(horizon)
    weighted = 0.0
    if items:
        # Используем 'value' (0-100) для более точного среднего
        avg_val = sum(it.get('value', 0.0) for it in items) / len(items)
        weighted = avg_val / 10.0 # переводим в 0-10
        
    # Округляем вверх, если есть хоть какой-то трафик > 1%, чтобы не было 0 при наличии машин
    score = int(round(weighted))
    if weighted > 0.1 and score == 0:
        score = 1

    return {
        "items": items,
        "overall_points": score,
        "horizon": horizon
    }


@app.get("/traffic/history")
def traffic_history(minutes: int = Query(60, ge=5, le=720)):
    conn = get_conn(settings.db_path)
    try:
        return {"items": get_history(conn, minutes)}
    finally:
        conn.close()


import json
from app.db.repository import get_road_segments

@app.get("/roads/segments")
def road_segments_api(horizon: int = Query(0, ge=0, le=60)):
    if horizon not in (0, 30, 60):
        return {"error": "horizon must be 0, 30, or 60"}
        
    conn = get_conn(settings.db_path)
    try:
        raw_segs = get_road_segments(conn)
    finally:
        conn.close()

    snapshot = sim.snapshot(horizon)
    loc_values = { s["location_id"]: s["value"] for s in snapshot }

    items = []
    for r in raw_segs:
        pts = []
        if r.get("polyline"):
            try:
                pts = json.loads(r["polyline"])
            except:
                pass
        
        lid = r["location_id"]
        val = loc_values.get(lid, 0.0)
        
        items.append({
            "id": r["id"],
            "name": r["name"],
            "location_id": lid,
            "polyline": pts,
            "value": val
        })
        
    return {"items": items}



@app.get("/traffic/accuracy")
def traffic_accuracy(
    horizon: int = Query(30, ge=0, le=60),
    minutes: int = Query(120, ge=30, le=720),
):
    """
    Рассчитывает метрики точности (MAE/RMSE) для моделей прогнозирования.
    """
    if horizon not in (0, 30, 60):
        return {"error": "horizon must be 0, 30, or 60"}
    if horizon == 0:
        return {"error": "metrics make sense for horizon=30/60"}

    conn = get_conn(settings.db_path)
    try:
        hist = get_history(conn, minutes)
    finally:
        conn.close()

    by_loc = group_by_location(hist)

    y_true_all = {"naive": [], "ma": [], "trend": []}
    y_pred_all = {"naive": [], "ma": [], "trend": []}

    for lid, series in by_loc.items():
        ts_to_val = {ts: v for ts, v in series}
        ts_list = [ts for ts, _ in series]

        for t in ts_list:
            target_t = t + horizon * 60
            if target_t not in ts_to_val:
                continue

            past = [(ts, ts_to_val[ts]) for ts in ts_list if ts <= t]
            if len(past) < 3:
                continue

            true_v = ts_to_val[target_t]

            pred1 = predict_naive(past)
            pred2 = predict_moving_avg(past, k=5)
            pred3 = predict_trend_lr(past, k=10, horizon_min=horizon)

            y_true_all["naive"].append(true_v)
            y_pred_all["naive"].append(pred1)

            y_true_all["ma"].append(true_v)
            y_pred_all["ma"].append(pred2)

            y_true_all["trend"].append(true_v)
            y_pred_all["trend"].append(pred3)

    return {
        "horizon": horizon,
        "minutes_used": minutes,
        "naive": mae_rmse(y_true_all["naive"], y_pred_all["naive"]),
        "moving_avg": mae_rmse(y_true_all["ma"], y_pred_all["ma"]),
        "trend_lr": mae_rmse(y_true_all["trend"], y_pred_all["trend"]),
    }


@app.get("/traffic/metrics")
def traffic_metrics_ui():
    """
    Возвращает текущий балл пробок (0-10) для мобильного приложения.
    """
    items = sim.snapshot(0)
    if not items:
        return {
            "global_score": 0,
            "level": "Нет данных",
            "description": "Данные о трафике временно недоступны"
        }
    
    # Считаем среднее по всем точкам города
    avg_val = sum(it.get('value', 0.0) for it in items) / len(items)
    score = int(round(avg_val / 10.0))
    if avg_val > 1.0 and score == 0:
        score = 1
    score = max(0, min(10, score))
    
    levels = [
        "Дороги свободны", "Дороги почти свободны", "Местами затруднения",
        "Местами пробки", "Движение плотное", "Затруднения в центре",
        "Серьёзные пробки", "Многокилометровые пробки", "Город стоит", "Транспортный коллапс"
    ]
    level = levels[score - 1] if 0 < score <= 10 else "Свободно"
    
    return {
        "global_score": score,
        "level": level,
        "description": f"В среднем по городу {score} балла. {level}."
    }


from app.predict import (
    group_by_location,
    predict_naive,
    predict_moving_avg,
    predict_trend_lr,
    mae_rmse,
    get_trend_analysis,
    detect_anomaly,
)

@app.get("/traffic/recommendation")
async def get_traffic_recommendation(location_id: int = Query(None)):
    """
    Генерирует умную рекомендацию (AI-совет) для пользователя с поиском аномалий.
    """
    conn = get_conn(settings.db_path)
    weather = await weather_service.get_current_weather()
    
    try:
        # Для простоты берем историю за час
        hist = get_history(conn, minutes=60)
        by_loc = group_by_location(hist)
        
        # Если location_id не передан, берем самую загруженную (hotspot) или среднюю
        if not location_id or location_id not in by_loc:
            # Найдем локу с самым крутым трендом вверх или просто рандомную из Астаны
            location_id = list(by_loc.keys())[0] if by_loc else 1
            
        loc_info = next((l for l in get_locations(conn) if l['id'] == location_id), {"name": "город"})
        series = by_loc.get(location_id, [])
        trend = get_trend_analysis(series)
        anomaly = detect_anomaly(series)
        
        # Строим текст совета
        wf = weather.get('traffic_factor', 1.0)
        
        # Если найдена аномалия - перебиваем обычный тренд
        if anomaly["anomaly"]:
            wait_time = anomaly["time_to_wait_min"]
            icon = "🚨" if anomaly["severity"] == "critical" else "⚠️"
            advice = f"{icon} AI АНАЛИЗ:\nНа участке «{loc_info['name']}» {anomaly['desc'].lower()} "
            advice += f"Советуем переждать около {wait_time} минут или найти пути объезда."
            
            return {
                "location_id": location_id,
                "location_name": loc_info['name'],
                "weather": weather['description'],
                "points_impact": 10,
                "trend": "Аномалия",
                "message": advice
            }

        # Обычная логика
        reason = []
        if trend['direction'] == 'up':
            reason.append(f"тренд на повышение трафика на {loc_info['name']}")
        if wf > 1.2:
            reason.append(f"прогнозируемые осадки ({weather['description']})")
            
        points_increase = int((wf - 1.0) * 5 + (2 if trend['direction'] == 'up' else 0))
        
        advice = "Рекомендую выехать сейчас."
        if points_increase > 2:
            advice = "Рекомендую выехать сейчас или подождать около 20-30 минут, пока ситуация стабилизируется."
        elif points_increase > 5:
            advice = "Ситуация сложная. Лучше воспользоваться общественным транспортом или отложить поездку на час."
            
        final_message = f"Судя по { ' и '.join(reason) if reason else 'текущей ситуации'}, пробка может вырасти на {points_increase} балла. {advice}"
        
        return {
            "location_id": location_id,
            "location_name": loc_info['name'],
            "weather": weather['description'],
            "points_impact": points_increase,
            "trend": trend['desc'],
            "message": final_message
        }
    finally:
        conn.close()

from app.vehicles import VehicleSimulator
veh_sim = VehicleSimulator(lambda: get_road_segments(get_conn(settings.db_path)))
veh_sim.start()

@app.get("/vehicles")
def get_vehicles():
    """
    Возвращает список машин и автобусов на карте.
    """
    return {"items": veh_sim.snapshot()}


# ─── Admin endpoints ───

from fastapi import Header, HTTPException
from pydantic import BaseModel
from app.auth import verify_admin_password, create_admin_token, verify_admin_token
from app.db.repository import (
    get_admin_by_login,
    get_friends,
    add_friend,
    commit,
)

class LoginRequest(BaseModel):
    login: str
    password: str

class AddFriendRequest(BaseModel):
    name: str


@app.post("/admin/login")
def admin_login(req: LoginRequest):
    conn = get_conn(settings.db_path)
    try:
        user = get_admin_by_login(conn, req.login)
        if not user or not verify_admin_password(user.get("password_hash"), req.password):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        token = create_admin_token(int(user["id"]))
        return {"token": token}
    finally:
        conn.close()


@app.get("/admin/dashboard")
def admin_dashboard(authorization: str = Header(None)):
    token = (authorization or "").replace("Bearer ", "")
    admin_id = verify_admin_token(token)
    if admin_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    conn = get_conn(settings.db_path)
    try:
        locations_count = conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
        segments_count = 0
        try:
            segments_count = conn.execute("SELECT COUNT(*) FROM road_segments").fetchone()[0]
        except Exception:
            pass
        friends_count = 0
        try:
            friends_count = conn.execute("SELECT COUNT(*) FROM friends").fetchone()[0]
        except Exception:
            pass

        # Текущий средний балл
        items = sim.snapshot(0)
        avg_val = 0.0
        if items:
            avg_val = sum(it.get('value', 0.0) for it in items) / len(items)

        return {
            "locations_count": locations_count,
            "segments_count": segments_count,
            "friends_count": friends_count,
            "sim_running": sim.is_running(),
            "hotspots": sim.hotspots_count(),
            "avg_traffic_value": round(avg_val, 1),
            "traffic_score": max(1, int(round(avg_val / 10.0))) if items else 0,
            "vehicles_count": len(veh_sim.snapshot()),
        }
    finally:
        conn.close()


@app.get("/friends")
def friends_list():
    conn = get_conn(settings.db_path)
    try:
        return {"items": get_friends(conn)}
    finally:
        conn.close()


@app.post("/friends")
def friends_add(req: AddFriendRequest):
    conn = get_conn(settings.db_path)
    try:
        fid = add_friend(conn, req.name)
        commit(conn)
        return {"id": fid, "name": req.name}
    finally:
        conn.close()


# ─── Seed data on startup ───

from app.seed import seed_locations_astana_if_empty, seed_segments_if_empty, seed_history_if_empty, seed_admin_if_empty

@app.on_event("startup")
def _seed():
    conn = get_conn(settings.db_path)
    try:
        seed_locations_astana_if_empty(conn)
        seed_segments_if_empty(conn)
        seed_history_if_empty(conn, sim)
        seed_admin_if_empty(conn)
    except Exception as e:
        print(f"Seed error: {e}")
    finally:
        conn.close()
