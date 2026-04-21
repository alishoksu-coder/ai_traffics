import httpx
import asyncio
import time

BASE_URL = "https://ai-traffics.onrender.com"
CONCURRENT_USERS = 50

async def fetch_locations(client, user_id):
    start = time.time()
    try:
        resp = await client.get(f"{BASE_URL}/locations", timeout=20.0)
        end = time.time()
        return resp.status_code, end - start
    except Exception as e:
        return "Error", 0

async def run_load_test():
    print(f"Запуск стресс-теста: {CONCURRENT_USERS} параллельных запросов к {BASE_URL}...")
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_locations(client, i) for i in range(CONCURRENT_USERS)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
    # Анализ результатов
    success_count = sum(1 for status, duration in results if status == 200)
    errors = [status for status, duration in results if status != 200]
    durations = [duration for status, duration in results if status == 200]
    
    print(f"\n--- Результаты стресс-теста ---")
    print(f"Всего запросов:    {CONCURRENT_USERS}")
    print(f"Успешно (200 OK):  {success_count}")
    print(f"Ошибок:            {len(errors)}")
    if durations:
        print(f"Среднее время:     {sum(durations)/len(durations):.2f} сек")
        print(f"Мин. время:        {min(durations):.2f} сек")
        print(f"Макс. время:       {max(durations):.2f} сек")
    print(f"Общее время теста: {total_time:.2f} сек")
    
    if success_count == CONCURRENT_USERS:
        print("\nИТОГ: Сервер отлично справился с нагрузкой!")
    elif success_count > CONCURRENT_USERS * 0.8:
        print("\nИТОГ: Сервер стабилен, но есть небольшие задержки при пиковой нагрузке.")
    else:
        print("\nИТОГ: Обнаружены проблемы при масштабировании. Бесплатный тариф Render может ограничивать потоки.")

if __name__ == "__main__":
    asyncio.run(run_load_test())
