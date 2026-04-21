import httpx
import asyncio
import json

BASE_URL = "https://ai-traffics.onrender.com"

async def run_scenarios():
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"\n--- [1] Получение узлов для маршрутизации ---")
        try:
            nodes_resp = await client.get(f"{BASE_URL}/routes/nodes")
            nodes = nodes_resp.json()["nodes"]
            print(f"Доступно узлов: {len(nodes)}")
            
            # Выбираем два узла для теста (например, Байтерек и Экспо)
            start_node_data = next(n for n in nodes if "Байтерек" in n["name"])
            end_node_data = next(n for n in nodes if "Экспо" in n["name"])
            
            start_node = start_node_data["node_id"]
            end_node = end_node_data["node_id"]
            print(f"Выбраны узлы: {start_node_data['name']} -> {end_node_data['name']}")
        except Exception as e:
            print(f"Ошибка при получении узлов: {e}")
            # Пытаемся взять любые два если поиск по имени не сработал
            nodes = nodes_resp.json()["nodes"]
            start_node = nodes[0]["node_id"]
            end_node = nodes[-1]["node_id"]
            print(f"Выбраны ID по умолчанию: {start_node} -> {end_node}")

        print(f"\n--- [2] Сравнение 4 режимов маршрутизации (TC-08 - TC-10) ---")
        modes = ["car_fast", "pedestrian", "barrier_free", "anti_stress"]
        results = {}
        
        for mode in modes:
            payload = {
                "start_node_id": start_node,
                "end_node_id": end_node,
                "mode": mode
            }
            try:
                resp = await client.post(f"{BASE_URL}/routes/calculate", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    results[mode] = data
                    print(f"Режим {mode.upper():<12}: {data['total_distance_m']:>7.1f}м, {data['estimated_time_min']:>5.1f} мин")
                else:
                    print(f"Ошибка режима {mode}: {resp.status_code}")
            except Exception as e:
                print(f"Сбой запроса для {mode}: {e}")

        print(f"\n--- [3] Симуляция Digital Twin (TC-11 - TC-12) ---")
        # 1. Запоминаем базовое время для авто
        base_time = results.get("car_fast", {}).get("estimated_time_min", 0)
        
        # 2. Создаем перекрытие (hotspot) прямо на пути
        # Используем координаты Байтерека
        print(f"Создаем инцидент (пробку) в точке старта...")
        closure_payload = {
            "lat": start_node_data["lat"],
            "lon": start_node_data["lon"],
            "duration_min": 15
        }
        await client.post(f"{BASE_URL}/traffic/simulate_closure", json=closure_payload)
        
        print("Ожидание обновления системы...")
        await asyncio.sleep(3)

        # 4. Пересчитываем маршрут
        print("Пересчитываем маршрут CAR_FAST после инцидента...")
        recalc_payload = {
            "start_node_id": start_node,
            "end_node_id": end_node,
            "mode": "car_fast"
        }
        recalc_resp = await client.post(f"{BASE_URL}/routes/calculate", json=recalc_payload)
        if recalc_resp.status_code == 200:
            new_data = recalc_resp.json()
            new_time = new_data['estimated_time_min']
            print(f"Базовое время: {base_time:.1f} мин")
            print(f"Новое время:   {new_time:.1f} мин")
            if new_time > base_time:
                diff = new_time - base_time
                print(f"РЕЗУЛЬТАТ: Время выросло на {diff:.1f} мин (+{int(diff/base_time*100)}%).")
                print("Система успешно имитирует реальное влияние пробок на ETA.")
            else:
                print("РЕЗУЛЬТАТ: Время не изменилось. Попробуйте создать инцидент в другой точке.")

if __name__ == "__main__":
    asyncio.run(run_scenarios())
