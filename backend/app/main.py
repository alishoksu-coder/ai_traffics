# backend/app/main.py
import os
import json
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Header, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.db.database import get_conn
from app.db.schema import ensure_schema
from app.db.repository import (
    get_locations,
    get_history,
    get_road_segments,
    get_admin_by_login,
    get_friends,
    add_friend,
    commit,
)
from app.simulate import TrafficSimulator

from app.predict import (
    group_by_location,
    predict_naive,
    predict_moving_avg,
    predict_trend_lr,
    predict_ema,
    mae_rmse,
    get_trend_analysis,
    detect_anomaly,
)
from app.weather import weather_service
from app.auth import verify_admin_password, create_admin_token, verify_admin_token
from app.vehicles import VehicleSimulator
from app.seed import (
    seed_locations_astana_if_empty,
    seed_segments_if_empty,
    seed_history_if_empty,
    seed_admin_if_empty,
)
from app.routing import routing_engine, NODES

try:
    from app.ai_worker import main_loop as start_ai_worker
except ImportError:
    start_ai_worker = None

sim = TrafficSimulator(settings.db_path, tick_seconds=2.0)

# --- VehicleSimulator с кэшированием соединения (фикс утечки #5) ---
_veh_segments_cache: list = []
_veh_cache_ts: float = 0

def _get_segments_cached() -> list:
    """Возвращает сегменты с кэшированием на 30 секунд, закрывая соединение."""
    import time
    global _veh_segments_cache, _veh_cache_ts
    now = time.time()
    if now - _veh_cache_ts > 30 or not _veh_segments_cache:
        conn = get_conn(settings.db_path)
        try:
            _veh_segments_cache = get_road_segments(conn)
        finally:
            conn.close()
        _veh_cache_ts = now
    return _veh_segments_cache

veh_sim = VehicleSimulator(_get_segments_cached)


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_conn(settings.db_path)
    try:
        ensure_schema(conn)
    finally:
        conn.close()

    # ✅ Seed data (перенесено из @app.on_event, который игнорируется при lifespan)
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

    sim.start()
    veh_sim.start()
    
    # Background weather update task
    async def update_weather_periodic():
        while True:
            w = await weather_service.get_current_weather()
            sim.set_weather_factor(w['traffic_factor'])
            await asyncio.sleep(600) # update every 10 min

    weather_task = asyncio.create_task(update_weather_periodic())
    
    # 🤖 Запускаем ИИ-Воркера для Supabase
    ai_task = None
    if start_ai_worker:
        ai_task = asyncio.create_task(start_ai_worker())
    
    try:
        yield
    finally:
        weather_task.cancel()
        if ai_task:
            ai_task.cancel()
        veh_sim.stop()
        sim.stop()


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Traffic Monitor API", version="0.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "cwd": os.getcwd(),
        "status": "ok",
        "sim_running": sim.is_running(),
        "hotspots": sim.hotspots_count(),
    }

@app.get("/parking")
def get_parking(horizon: int = Query(0, ge=0, le=120)):
    """
    Возвращает список умных парковок (Smart Parking) с AI-анализом свободных мест.
    С учетом горизонта прогнозирования трафика: чем больше пробок, тем меньше мест.
    """
    import random
    import time
    parkings = [
        {"id": 1, "name": "ТРЦ Хан Шатыр", "lat": 51.1326, "lng": 71.4037, "capacity": 200, "price": "200 ₸/сағ"},
        {"id": 2, "name": "Бәйтерек Монументі", "lat": 51.1283, "lng": 71.4304, "capacity": 150, "price": "300 ₸/сағ"},
        {"id": 3, "name": "Астана Опера", "lat": 51.1256, "lng": 71.4162, "capacity": 80, "price": "Тегін (Бесплатно)"},
        {"id": 4, "name": "MEGA Silk Way", "lat": 51.0888, "lng": 71.4187, "capacity": 500, "price": "100 ₸/сағ"},
        {"id": 5, "name": "Abu Dhabi Plaza", "lat": 51.1197, "lng": 71.4390, "capacity": 300, "price": "500 ₸/сағ"},
        {"id": 6, "name": "Керуен (Keruen)", "lat": 51.1281, "lng": 71.4248, "capacity": 120, "price": "400 ₸/сағ"}
    ]
    
    # Предиктивный фактор загруженности
    trend_factor = 1.0
    message = None
    if horizon > 0:
        # Snap horizon to 30 or 60 for snapshot
        snap_h = 30 if horizon <= 45 else 60
        snapshot = sim.snapshot(snap_h)
        if snapshot:
            avg_traffic = sum(s.get('value', 0) for s in snapshot) / len(snapshot) if snapshot else 0
            if avg_traffic > 60:  # value is 0-100
                trend_factor = 1.4
                message = f"Болжам (через {horizon} мин): Кептеліске байланысты бос орындар аз болады."
            elif avg_traffic < 30:
                trend_factor = 0.6
                message = f"Болжам (через {horizon} мин): Жолдар бос, парковкада орындар көп."
            else:
                message = f"Болжам (через {horizon} мин): Қалыпты жүктеме күтілуде."
    
    # Симулируем занятость. Используем время для некоторого изменения
    random.seed(int(time.time() / 300) + horizon)
    for p in parkings:
        base_occupancy = random.uniform(0.3, 0.7) * p["capacity"]
        occupied = int(base_occupancy * trend_factor)
        if occupied >= p["capacity"]:
            occupied = int(p["capacity"] * 0.98)
        p["occupied"] = occupied
        p["available"] = p["capacity"] - p["occupied"]
        p["status"] = "Бос (Свободно)" if p["available"] > 20 else ("Толы (Мало мест)" if p["available"] > 0 else "Орын жоқ (Нет мест)")
        
    res = {"items": parkings}
    if message:
        res["message"] = message
    return res


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
            except Exception:
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


@app.get("/traffic/ar_points")
def traffic_ar_points(horizon: int = Query(30, ge=0, le=60)):
    """
    Возвращает список «проблемных зон» с координатами для AR/Street View визуализации.
    Точки, где прогнозируется высокий уровень загруженности.
    """
    if horizon not in (0, 30, 60):
        return {"error": "horizon must be 0, 30, or 60"}

    conn = get_conn(settings.db_path)
    try:
        raw_segs = get_road_segments(conn)
    finally:
        conn.close()

    snapshot = sim.snapshot(horizon)
    loc_values = {s["location_id"]: s["value"] for s in snapshot}

    ar_points = []
    for r in raw_segs:
        lid = r["location_id"]
        val = loc_values.get(lid, 0.0)

        # Только сегменты с загруженностью > 50% считаются «проблемными»
        if val < 50:
            continue

        pts = []
        if r.get("polyline"):
            try:
                pts = json.loads(r["polyline"])
            except Exception:
                pass

        if not pts:
            continue

        # Берём середину сегмента как точку визуализации
        mid = pts[len(pts) // 2]
        level = "critical" if val >= 80 else "warning"
        speed_est = max(3, int(60 * (1 - val / 100)))  # примерная скорость потока

        ar_points.append({
            "lat": mid[0] if isinstance(mid, list) else mid.get("lat", 0),
            "lng": mid[1] if isinstance(mid, list) else mid.get("lng", 0),
            "segment_name": r["name"],
            "congestion_value": round(val, 1),
            "level": level,
            "speed_kmh": speed_est,
            "message": f"Болжам: жылдамдық {speed_est} км/сағ дейін төмендейді" if level == "critical"
                       else f"Қозғалыс баяулайды, ~{speed_est} км/сағ"
        })

    return {"horizon": horizon, "ar_points": ar_points}



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


@app.get("/traffic/recommendation")
async def get_traffic_recommendation(location_id: int = Query(None)):
    """
    Генерирует умную рекомендацию (AI-совет) для пользователя.
    """
    conn = get_conn(settings.db_path)
    weather = await weather_service.get_current_weather()
    
    try:
        hist = get_history(conn, minutes=60)
        by_loc = group_by_location(hist)
        
        if not location_id or location_id not in by_loc:
            location_id = list(by_loc.keys())[0] if by_loc else 1
            
        loc_info = next((l for l in get_locations(conn) if l['id'] == location_id), {"name": "город"})
        series = by_loc.get(location_id, [])
        
        # New analysis
        trend = get_trend_analysis(series)
        anomaly = detect_anomaly(series)
        target_ema = predict_ema(series, alpha=0.4)
        lr_pred = predict_trend_lr(series, k=15, horizon_min=30)
        
        wf = weather.get('traffic_factor', 1.0)
        current_val = series[-1][1] if series else 0.0
        
        # If there's an anomaly, completely override
        if anomaly["anomaly"]:
            wait_time = anomaly["time_to_wait_min"]
            icon = "🚨" if anomaly["severity"] == "critical" else "⚠️"
            desc = anomaly['desc']
            advice = (f"{icon} AI АНАЛИЗ МАРШРУТА:\n"
                      f"Участок «{loc_info['name']}» нестабилен. {desc} "
                      f"Модель рекомендует отложить поездку на {wait_time} минут или использовать объезд, "
                      f"так как скользящая средняя (EMA) показывает аномальный скачок загруженности.")
            return {
                "location_id": location_id,
                "location_name": loc_info['name'],
                "weather": weather['description'],
                "points_impact": 10,
                "trend": "Аномалия",
                "message": advice
            }

        # Human-like AI generation text
        points_increase = max(0, int((lr_pred - current_val) / 10.0))
        if wf > 1.2:
            points_increase += 2

        weather_txt = f"осадков ({weather['description']})" if wf > 1.2 else "благоприятной погоды"
        
        if current_val < 30 and points_increase < 2:
            msg = (f"✨ AI АНАЛИЗ МАРШРУТА:\n"
                   f"Отличные новости! Модель предсказывает свободные дороги на участке «{loc_info['name']}». "
                   f"Тренд {trend['desc'].lower()}, а прогноз по математической регрессии не обещает заторов. "
                   f"С учетом {weather_txt}, сейчас идеальное время для выезда.")
        elif current_val < 60 and points_increase <= 3:
            msg = (f"📊 AI АНАЛИЗ МАРШРУТА:\n"
                   f"Рабочий трафик на «{loc_info['name']}». Текущая загруженность умеренная. "
                   f"Наш алгоритм ожидает рост на ~{points_increase} балла к моменту прибытия "
                   f"(учитывая фактор {weather_txt}). Советую выезжать сейчас, пока ситуация не ухудшилась.")
        elif current_val >= 60 and points_increase <= 2:
            msg = (f"⏳ AI АНАЛИЗ МАРШРУТА:\n"
                   f"Движение на «{loc_info['name']}» уже плотное. Тренд: {trend['desc'].lower()}. "
                   f"EMA-сглаживание графиков показывает стабильное напряжение без резких скачков. "
                   f"Можете ехать, но заложите дополнительные 10-15 минут в пути.")
        else:
            msg = (f"🛑 AI АНАЛИЗ МАРШРУТА:\n"
                   f"Не лучшее время для поездки через «{loc_info['name']}». "
                   f"AI-модель прогнозирует дальнейшее ухудшение ситуации (тренд {trend['desc'].lower()}). "
                   f"Ожидается рост пробки на {points_increase} балла из-за {weather_txt}. "
                   f"Рекомендуем выпить кофе и переждать 30-40 минут.")

        return {
            "location_id": location_id,
            "location_name": loc_info['name'],
            "weather": weather['description'],
            "points_impact": points_increase,
            "trend": trend['desc'],
            "message": msg
        }
    finally:
        conn.close()

class SimulationRequest(BaseModel):
    lat: float
    lon: float
    duration_min: int = 15

@app.post("/traffic/simulate_closure")
def simulate_closure(req: SimulationRequest):
    """
    Режим «Цифровой двойник» (What-If Engine).
    Искусственно блокирует/замедляет дорогу по переданным координатам.
    """
    # Создаем аномальный очаг (strength=95.0 - почти полная остановка)
    sim.add_custom_hotspot(req.lat, req.lon, strength=95.0, radius_deg=0.012, ttl_seconds=req.duration_min * 60)
    return {
        "status": "success",
        "message": f"Очаг пробки успешно создан. Действует {req.duration_min} мин."
    }

class MultimodalRequest(BaseModel):
    duration_now_sec: int
    distance_meters: int

@app.post("/traffic/multimodal_analysis")
async def multimodal_analysis(req: MultimodalRequest):
    """
    Бизнес-логика мультимодальных маршрутов.
    T1 = Текущее время на авто
    T2 = Время на авто через 20/30 минут (прогноз)
    T3 = Время по мультимодальному пути (авто + самокат/пешком)
    """
    t1 = req.duration_now_sec
    
    # Симуляция: проверяем средний балл трафика впереди
    items = sim.snapshot(30)
    avg_future_traffic = 0.0
    if items:
        avg_future_traffic = sum(it.get('value', 0.0) for it in items) / len(items)
        
    # Если пробки будут расти (например, future traffic > 50%), время увеличится
    traffic_multiplier = 1.0 + (avg_future_traffic / 100.0) * 0.5
    t2 = int(t1 * traffic_multiplier)
    
    # Мультимодальный путь: допустим, едем на машине 60% пути, затем берем самокат.
    # Машина (60%): без симуляции пробок на дальнем участке
    # Самокат (40%): скорость фиксированная ~15 км/ч (4 м/с)
    car_distance = req.distance_meters * 0.6
    scooter_distance = req.distance_meters * 0.4
    
    # На авто первая часть (предположим пробки еще не собрались): 
    # Средняя скорость ~ 30 км/ч = 8.33 м/с
    car_time = car_distance / 8.33
    scooter_time = scooter_distance / 4.0
    
    # Плюс время на пересадку ~ 3 минуты (180 сек)
    t3 = int(car_time + scooter_time + 180)
    
    # Если изначально расстояние очень короткое (меньше 2 км), самокат выгоднее сразу
    if req.distance_meters < 2000:
        t3 = int(req.distance_meters / 4.0)

    recommend = t3 < t2
    
    return {
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "recommend_transfer": recommend,
        "scooter_distance": int(scooter_distance),
        "message": f"С учетом будущего затора, комбинированный маршрут сэкономит {max(0, (t2 - t3)//60)} минут." if recommend else "Оставайтесь на текущем маршруте."
    }

class RouteCalculateRequest(BaseModel):
    start_node_id: int
    end_node_id: int
    mode: str = "car_fast"  # car_fast, pedestrian, barrier_free, anti_stress
    horizon_min: int = 0    # Traffic prediction horizon in minutes

@app.post("/routes/calculate")
def calculate_multicriteria_route(req: RouteCalculateRequest):
    """
    Рассчитывает оптимальный путь с использованием AI болжам (предсказания пробок)
    и физических/психологических факторов (кедергісіз, антистресс).
    """
    if req.start_node_id not in NODES or req.end_node_id not in NODES:
        raise HTTPException(status_code=400, detail="Invalid node IDs")
        
    # Get AI Traffic prediction if mode is car_fast or anti_stress
    traffic_map = {}
    if req.mode in ["car_fast", "anti_stress"] or req.horizon_min > 0:
        # Snap horizon to nearest supported format
        snap_h = 30 if 15 <= req.horizon_min <= 45 else (60 if req.horizon_min > 45 else 0)
        snapshot = sim.snapshot(snap_h)
        if snapshot:
            # location_id to value 0-100
            for item in snapshot:
                loc_id = item.get("location_id")
                # Map location_id from DB to our graph Node ID safely
                # (For demo purposes, our node IDs match location IDs 1, 2, 3)
                if loc_id in NODES:
                    traffic_map[loc_id] = item.get("value", 0.0)

    # Route!
    res = routing_engine.calculate_route(req.start_node_id, req.end_node_id, req.mode, traffic_map)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
        
    return res

@app.get("/routes/nodes")
def get_routing_nodes():
    """
    Возвращает список доступных точек (вершин графа) для тестирования маршрутизатора.
    """
    return {"nodes": [n.__dict__ for n in NODES.values()]}

@app.get("/vehicles")
def get_vehicles():
    """
    Возвращает список машин и автобусов на карте.
    """
    return {"items": veh_sim.snapshot()}


# ─── Admin endpoints ───

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


@app.post("/admin/register")
def admin_register(req: LoginRequest):
    from app.auth import hash_for_storage
    from app.db.repository import create_admin
    conn = get_conn(settings.db_path)
    try:
        user = get_admin_by_login(conn, req.login)
        if user:
            raise HTTPException(status_code=400, detail="Мұндай логин тіркелген (User already exists)")
        
        hashed = hash_for_storage(req.password)
        create_admin(conn, req.login, hashed)
        commit(conn)
        
        # Сразу возвращаем токен авторизации
        user_new = get_admin_by_login(conn, req.login)
        token = create_admin_token(int(user_new["id"]))
        return {"token": token, "message": "Тіркелу сәтті аяқталды"}
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
