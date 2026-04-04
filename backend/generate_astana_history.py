# backend/generate_astana_history.py
import csv
import random
from datetime import datetime, timedelta

def get_traffic_value(hour, segment_id, day_of_week):
    base = 10.0
    if 7 <= hour <= 9:
        base = 75.0 if segment_id % 2 == 0 else 50.0
        if hour == 8: base += 15.0
    elif 17 <= hour <= 19:
        base = 80.0 if segment_id % 2 != 0 else 55.0
        if hour == 18: base += 15.0
    elif 12 <= hour <= 14:
        base = 45.0
    if day_of_week >= 5:
        if 12 <= hour <= 20: base = 60.0
        else: base = 15.0
    noise = random.uniform(-10, 10)
    return max(0.0, min(100.0, base + noise))

def main():
    print("🚀 Генерация 20,000 записей для Астаны...")
    
    filename = "astana_traffic_history_20k.csv"
    segment_ids = list(range(1, 41)) # 40 сегментов
    days_to_generate = 21 # 3 недели
    
    records = []
    start_dt = datetime.now() - timedelta(days=days_to_generate)
    
    # Генерируем ~20,000 записей
    for day in range(days_to_generate):
        for hour in range(24):
            for minute in [0, 30]:
                dt = start_dt + timedelta(days=day, hours=hour, minutes=minute)
                day_of_week = dt.weekday()
                for sid in segment_ids:
                    records.append({
                        "segment_id": sid,
                        "value": round(get_traffic_value(hour, sid, day_of_week), 2),
                        "created_at": dt.strftime("%Y-%m-%d %H:%M:%S")
                    })

    # Сохраняем в CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["segment_id", "value", "created_at"])
        writer.writeheader()
        writer.writerows(records)

    print(f"✅ Файл создан: {filename}")
    print(f"📊 Всего записей: {len(records)}")
    print("\nПервые 10 строк:")
    for r in records[:10]:
        print(r)

if __name__ == "__main__":
    main()
