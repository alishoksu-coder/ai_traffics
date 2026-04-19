import json
import random
import math
import os
import heapq

# --- 1. ГЕНЕРАЦИЯ ДАТАСЕТА (ЦИФРОВОЙ КЛОН) ---

# Координаты Водно-Зеленого Бульвара (от Акорды до Хан Шатыра)
LAT_MIN = 51.120
LAT_MAX = 51.135
LON_MIN = 71.420
LON_MAX = 71.445

GRID_SIZE_X = 100
GRID_SIZE_Y = 100

def haversine_distance(lat1, lon1, lat2, lon2):
    """Вычисляет расстояние в метрах между двумя координатами."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def generate_yesil_clone():
    nodes = {}
    node_id = 1
    
    # Генерация узлов (перекрестков и пешеходных точек)
    for i in range(GRID_SIZE_X):
        for j in range(GRID_SIZE_Y):
            lat = LAT_MIN + (LAT_MAX - LAT_MIN) * (i / max(1, GRID_SIZE_X - 1))
            lon = LON_MIN + (LON_MAX - LON_MIN) * (j / max(1, GRID_SIZE_Y - 1))
            
            name = "Тротуар"
            if i == 0 and j == 0: name = "Хан Шатыр"
            if i == GRID_SIZE_X // 2 and j == GRID_SIZE_Y // 2: name = "Байтерек"
            if i == GRID_SIZE_X - 1 and j == GRID_SIZE_Y - 1: name = "Акорда"
            
            nodes[node_id] = {
                "id": node_id,
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "name": f"{name} (Узел {node_id})"
            }
            node_id += 1
            
    edges = []
    # Генерация ребер (дорожек между узлами)
    for i in range(1, len(nodes) + 1):
        # Соединяем с правым соседом
        if i % GRID_SIZE_Y != 0:
            neighbor = i + 1
            dist = haversine_distance(nodes[i]["lat"], nodes[i]["lon"], nodes[neighbor]["lat"], nodes[neighbor]["lon"])
            
            # Эмуляция инфраструктуры: 20% дорог имеют лестницы, 80% дорог с пандусами
            has_stairs = random.random() < 0.2
            edges.append({
                "from": i,
                "to": neighbor,
                "distance_m": round(dist, 1),
                "has_ramp": random.random() > 0.3, # 70% шанс хорошего съезда
                "stairs_count": random.randint(5, 15) if has_stairs else 0,
                "surface_quality": random.randint(3, 10) # 10 - идеальный асфальт
            })
            # Дорога в обе стороны
            edges.append({
                "from": neighbor,
                "to": i,
                "distance_m": round(dist, 1),
                "has_ramp": random.random() > 0.3,
                "stairs_count": random.randint(5, 15) if has_stairs else 0,
                "surface_quality": random.randint(3, 10)
            })
            
        # Соединяем с нижним соседом
        if i + GRID_SIZE_Y <= len(nodes):
            neighbor = i + GRID_SIZE_Y
            dist = haversine_distance(nodes[i]["lat"], nodes[i]["lon"], nodes[neighbor]["lat"], nodes[neighbor]["lon"])
            has_stairs = random.random() < 0.2
            edges.append({
                "from": i,
                "to": neighbor,
                "distance_m": round(dist, 1),
                "has_ramp": random.random() > 0.3,
                "stairs_count": random.randint(5, 15) if has_stairs else 0,
                "surface_quality": random.randint(3, 10)
            })
            edges.append({
                "from": neighbor,
                "to": i,
                "distance_m": round(dist, 1),
                "has_ramp": random.random() > 0.3,
                "stairs_count": random.randint(5, 15) if has_stairs else 0,
                "surface_quality": random.randint(3, 10)
            })

    # Сохраняем датасет
    os.makedirs("data", exist_ok=True)
    with open("data/yesil_accessibility.json", "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=2)
        
    print(f"DONE: Цифровой клон Есильского района успешно сгенерирован!")
    print(f"Сохранено узлов: {len(nodes)}, Сохранено путей: {len(edges)}")
    return nodes, edges

# --- 2. АЛГОРИТМ ИНКЛЮЗИВНОЙ НАВИГАЦИИ (A* Star) ---

def find_barrier_free_route(nodes, edges, start_id, end_id, barrier_free=True):
    """
    Алгоритм Дейкстры / A*, который учитывает физические барьеры цифрового двойника.
    """
    graph = {n: [] for n in nodes.keys()}
    for e in edges:
        graph[e["from"]].append(e)

    # Очередь с приоритетом: (cost, current_node, path)
    pq = [(0, start_id, [])]
    visited = set()

    while pq:
        cost, curr, path = heapq.heappop(pq)
        
        if curr in visited:
            continue
        visited.add(curr)
        path = path + [curr]

        if curr == end_id:
            return path, cost

        for edge in graph[curr]:
            nxt = edge["to"]
            
            # Если юзер включил "Кедергісіз" (Для колясок), 
            # мы СТРОГО запрещаем пути с лестницами и штрафуем за плохой асфальт/отсутствие пандусов.
            if barrier_free:
                if edge["stairs_count"] > 0:
                    continue  # Проход для коляски закрыт!
                
                # Рассчитываем виртуальную "стоимость" пути (Penalty)
                penalty = edge["distance_m"]
                if not edge["has_ramp"]:
                    penalty += 300  # Штраф 300 метров за высокий бордюр
                penalty += (10 - edge["surface_quality"]) * 10 # Штраф за плохую дорогу
                
                new_cost = cost + penalty
            else:
                # Обычный пешеход: расстояние в приоритете, лестницы не помеха
                new_cost = cost + edge["distance_m"]

            if nxt not in visited:
                heapq.heappush(pq, (new_cost, nxt, path))

    return None, float('inf')

if __name__ == "__main__":
    nodes, edges = generate_yesil_clone()
    
    # Демонстрация работы алгоритма для Диплома
    # Ищем путь от Хан Шатыра (Узел 1) до Байтерека (Узел 55 или середина сетки)
    start_node = 1
    end_node = (GRID_SIZE_X * GRID_SIZE_Y) // 2 + (GRID_SIZE_X // 2)

    print("\n--- ТЕСТИРОВАНИЕ МАРШРУТОВ (СИМУЛЯЦИЯ) ---")
    
    normal_path, norm_cost = find_barrier_free_route(nodes, edges, start_node, end_node, barrier_free=False)
    print(f"--- Обычный пешеход ---")
    print(f"   Длина пути (виртуальные метры): {round(norm_cost, 1)}")
    print(f"   Количество узлов пройдено: {len(normal_path) if normal_path else 0}")
    
    inclusive_path, incl_cost = find_barrier_free_route(nodes, edges, start_node, end_node, barrier_free=True)
    print(f"\n--- Инвалидная коляска (Barrier-Free AI) ---")
    if inclusive_path:
        print(f"   Интеллектуальная стоимость пути: {round(incl_cost, 1)}")
        print(f"   Количество узлов пройдено: {len(inclusive_path)}")
        
        # Сравниваем
        if normal_path != inclusive_path:
            print("   >>> ВАУ! Система распознала препятствия (лестницы/бордюры)")
            print("       и построила безопасный обходной маршрут в обход стандартному!")
        else:
            print("   Маршруты совпали, дополнительных преград нет.")
    else:
        print("   Внимание: Из-за полного отсутствия пандусов или наличия лестниц вокруг,")
        print("   безопасный путь для коляски построить невозможно. (Digital Twin выявил проблему городской среды!)")
