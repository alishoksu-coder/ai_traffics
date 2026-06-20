# backend/app/services/ml_service.py
"""
Сервис для работы с ML-моделями: получение рекомендаций по трафику и метрик.
"""
from app.repositories.model_metrics_repository import get_latest_metrics_by_horizon
from app.repositories.traffic_repository import get_history, get_locations
from app.ml.preprocessing import group_by_location, get_trend_analysis, detect_anomaly
from app.ml.predictor import predict_ema, predict_trend_lr
from app.weather import weather_service
import sqlite3

async def get_traffic_recommendation(conn: sqlite3.Connection, location_id: int):
    """
    Генерирует умную рекомендацию (AI-совет) для пользователя.
    """
    weather = await weather_service.get_current_weather()
    
    hist = get_history(conn, minutes=60)
    by_loc = group_by_location(hist)
    
    if not location_id or location_id not in by_loc:
        location_id = list(by_loc.keys())[0] if by_loc else 1
        
    loc_info = next((l for l in get_locations(conn) if l['id'] == location_id), {"name": "город"})
    series = by_loc.get(location_id, [])
    
    trend = get_trend_analysis(series)
    anomaly = detect_anomaly(series)
    target_ema = predict_ema(series, alpha=0.4)
    lr_pred = predict_trend_lr(series, k=15, horizon_min=30)
    
    wf = weather.get('traffic_factor', 1.0)
    current_val = series[-1][1] if series else 0.0
    
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

def get_model_metrics(conn: sqlite3.Connection, horizon: int):
    return get_latest_metrics_by_horizon(conn, horizon)
