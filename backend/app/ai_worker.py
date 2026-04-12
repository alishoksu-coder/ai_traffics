import time
import httpx
import asyncio
from datetime import datetime
import sqlite3
import os
import xml.etree.ElementTree as ET

from app.config import settings
from app.predict import (
    group_by_location,
    predict_ema,
    predict_trend_lr,
    get_trend_analysis,
    detect_anomaly,
)
from app.weather import weather_service
from app.ai_brain import ai_brain

# --- КОНФИГУРАЦИЯ SUPABASE ---
SUPABASE_URL = "https://nxmefixitnmfzgaxlzsl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im54bWVmaXhpdG5tZnpnYXhsenNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NjIzNzYsImV4cCI6MjA4OTQzODM3Nn0.g-fY2uUmraHS-Vs9zLcoF1mPuwnhlZzHPlrR_cYXOTU"

DB_PATH = settings.db_path
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(os.getcwd(), DB_PATH)

_cycle_count = 0

async def push_to_supabase(table: str, data: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json=data, headers=headers)
        except Exception as e:
            print(f"Supabase Error: {e}")

async def get_2gis_traffic_score():
    """Функция для получения балла пробок из 2GIS (приоритетный источник)"""
    url = "https://catalog.api.2gis.ru/3.0/items/byid?id=70000001093468905&key=c7f1a769-c8a5-4636-b14d-d8c987808a12&locale=ru_KZ&fields=items.locale,items.flags,items.search_attributes.detection_type,items.search_attributes.additional_info,search_attributes,items.search_attributes.relevance,items.adm_div,items.city_alias,items.region_id,items.segment_id,items.reviews,items.point,request_type,context_rubrics,query_context,items.links,items.name_ex,items.name_back,items.org,items.group,items.dates,items.external_content,items.contact_groups,items.comment,items.ads.options,items.email_for_sending.allowed,items.stat,items.stop_factors,items.description,items.geometry.centroid,items.geometry.selection,items.geometry.style,items.timezone_offset,items.context,items.level_count,items.address,items.is_paid,items.access,items.access_comment,items.for_trucks,items.is_incentive,items.paving_type,items.capacity,items.schedule,items.schedule_special,items.floors,items.floor_id,items.floor_plans,ad,items.rubrics,items.routes,items.platforms,items.directions,items.barrier,items.reply_rate,items.purpose,items.purpose_code,items.attribute_groups,items.route_logo,items.has_goods,items.has_apartments_info,items.has_pinned_goods,items.has_realty,items.has_otello_stories,items.has_exchange,items.has_payments,items.has_dynamic_congestion,items.is_promoted,items.congestion,items.delivery,items.order_with_cart,search_type,items.has_discount,items.metarubrics,items.detailed_subtype,items.temporary_unavailable_atm_services,items.poi_category,items.has_ads_model,items.vacancies,items.structure_info.material,items.structure_info.floor_type,items.structure_info.gas_type,items.structure_info.year_of_construction,items.structure_info.elevators_count,items.structure_info.is_in_emergency_state,items.structure_info.project_type,items.has_otello_hotels,items.ski_lift,items.ski_track,items.inactive,items.links,items.source_url,items.statistics,items.geo_attributes,items.seasonal&stat%5Bsid%5D=f7d1c5d7-3fc5-4173-9f25-6c78a8748e4f&stat%5Buser%5D=cc740ae1-988c-4a31-999f-18ce9df18348&shv=2026-04-07-23&r=113030112"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru,en-US;q=0.9,en;q=0.8,kk;q=0.7",
        "cache-control": "no-cache",
        "origin": "https://2gis.kz",
        "pragma": "no-cache",
        "referer": "https://2gis.kz/",
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, headers=headers, timeout=7.0)
            if r.status_code == 200:
                data = r.json()
                items = data.get('result', {}).get('items', [])
                if items:
                    congestion = items[0].get('congestion')
                    # Если congestion есть, но там None или это пустой объект - значит пробок 0 баллов
                    if congestion is None:
                        return 0
                    return int(congestion.get('level', 0))
                return 0 # Если айтем найден, но данных нет - считаем пробки нулевыми
        except Exception as e:
            print(f"2GIS Traffic API Error: {e}")
    return None

async def get_yandex_traffic_score():
    """Функция для получения балла пробок из Яндекса (резервный источник)"""
    url = "https://export.yandex.ru/bar/reginfo.xml?region=163"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, timeout=5.0)
            if r.status_code == 200:
                root = ET.fromstring(r.text)
                level = root.find(".//level")
                if level is not None:
                    return int(level.text)
        except Exception as e:
            print(f"Yandex Traffic API Error: {e}")
    return 0

async def get_real_traffic_score():
    """Получает реальный балл пробок для Астаны, используя 2GIS как основной и Яндекс как запасной источники"""
    # 1. Сначала пробуем 2GIS
    score = await get_2gis_traffic_score()
    if score is not None:
        print(f"📡 Данные успешно получены из 2GIS: {score} баллов.")
        return score
    
    # 2. Если 2GIS подвел, идем в Яндекс
    print("⚠️ 2GIS недоступен, используем Яндекс как fallback...")
    return await get_yandex_traffic_score()

def get_local_history(minutes=60):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = int(time.time())
    since = now - (minutes * 60)
    cur.execute("SELECT location_id, ts, value FROM traffic_values WHERE ts > ?", (since,))
    rows = cur.fetchall()
    conn.close()
    return [{"location_id": r[0], "ts": r[1], "value": r[2]} for r in rows]

def save_real_experience(lid, value, wf):
    """Сохраняет реальные данные в БД, чтобы ИИ на них обучался"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ts = int(time.time())
    cur.execute(
        "INSERT INTO traffic_values (location_id, ts, value, weather_factor) VALUES (?,?,?,?)",
        (lid, ts, value, wf)
    )
    conn.commit()
    conn.close()

async def process_ai_logic():
    global _cycle_count
    
    # Первое обучение сразу при запуске
    if _cycle_count == 0:
        print("🧠 ИИ-Воркер: Первичное обучение модели...")
        ai_brain.train_on_history()
    
    _cycle_count += 1
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ИИ-Воркер: Анализ РЕАЛЬНОГО трафика Астаны...")
    
    # 1. Тянем живую ситуацию из Яндекса
    real_score = await get_real_traffic_score() # 0-10
    percent_score = real_score * 10.0 # 0-100%
    
    weather = await weather_service.get_current_weather()
    wf = weather.get('traffic_factor', 1.0)
    
    # 2. Обучение: каждые 15 минут (при цикле 45с это ~20 итераций)
    if _cycle_count % 20 == 0:
        print("🧠 ИИ-Воркер: Плановое дообучение модели...")
        ai_brain.train_on_history()

    # 3. Сохраняем опыт для обучения (сегмент 1 - представим как средний по городу)
    save_real_experience(1, percent_score, wf)

    # 4. Делаем прогноз (на 1 час вперед)
    now_dt = datetime.now()
    ml_pred = ai_brain.predict(1, now_dt.hour, now_dt.weekday(), wf)
    
    # 5. Формируем рекомендацию на основе ИИ
    if percent_score < 30:
        msg = f"✨ Живой балл: {real_score}. Дороги свободны. ИИ подтверждает: это лучшее время для поездки по Астане!"
    elif percent_score < 60:
        msg = f"📊 Живой балл: {real_score}. Дороги умеренно загружены. ИИ предсказывает {int(ml_pred/10)} баллов через час."
    elif percent_score < 85:
        msg = f"🛑 ВНИМАНИЕ: Пробки растут ({real_score} баллов). ИИ советует выезжать сейчас или ждать 2 часа."
    else:
        msg = f"💀 Астана стоит! {real_score} баллов. ИИ предсказывает коллапс. Оставайтесь в безопасности."

    # 6. Отправка в Supabase для мобильного приложения
    await push_to_supabase("traffic_history", {"segment_id": 1, "value": percent_score})
    await push_to_supabase("ai_recommendations", {
        "segment_id": 1,
        "message": msg,
        "trend": "Стабильно" if abs(ml_pred - percent_score) < 15 else ("Растет" if ml_pred > percent_score else "Спадает"),
        "points_impact": int(percent_score / 10),
        "weather_desc": weather['description']
    })

    print(f"ИИ-Воркер: Реальный балл {real_score}/10 учтен. Статистика: {_cycle_count} итераций.")

async def main_loop():
    while True:
        try:
            await process_ai_logic()
        except Exception as e:
            print(f"Worker Error: {e}")
        await asyncio.sleep(45)

if __name__ == "__main__":
    asyncio.run(main_loop())
