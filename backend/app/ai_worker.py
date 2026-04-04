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

async def get_real_traffic_score():
    """Получает реальный балл пробок для Астаны из Яндекса"""
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
