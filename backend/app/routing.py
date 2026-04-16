# backend/app/routing.py
import math
import heapq
from typing import List, Dict, Tuple

class Node:
    def __init__(self, node_id: int, name: str, lat: float, lon: float):
        self.node_id = node_id
        self.name = name
        self.lat = lat
        self.lon = lon

class Edge:
    def __init__(self, source: int, target: int, distance_m: float, 
                 has_stairs: bool, nature_score: float, car_allowed: bool, 
                 base_speed_kmh: float):
        self.source = source
        self.target = target
        self.distance_m = distance_m
        self.has_stairs = has_stairs
        self.nature_score = nature_score # 0 to 10
        self.car_allowed = car_allowed
        self.base_speed_kmh = base_speed_kmh

# Hardcoded simplified graph for Yesil region simulation
NODES = {
    1: Node(1, "Байтерек", 51.1283, 71.4305),
    2: Node(2, "Экспо", 51.0903, 71.4182),
    3: Node(3, "Хан Шатыр", 51.1325, 71.4038),
    101: Node(101, "Ботанический Сад", 51.1147, 71.4146),
    102: Node(102, "Абу Даби Плаза", 51.1197, 71.4390),
    103: Node(103, "Триумфальная Арка", 51.1044, 71.4369),
    104: Node(104, "Керуен (Talan Towers)", 51.1281, 71.4248)
}

# Undirected graph defined as list of edges
_RAW_EDGES = [
    # 1. Bayterek to Keruen: Short walk, but underpass has stairs
    Edge(1, 104, distance_m=500, has_stairs=True, nature_score=2.0, car_allowed=True, base_speed_kmh=40),
    
    # 2. Bayterek to Khan Shatyr: Long avenue (Nurzhol Blvd) pedestrian + road
    Edge(1, 3, distance_m=1800, has_stairs=False, nature_score=5.0, car_allowed=True, base_speed_kmh=50),
    
    # 3. Keruen to Abu Dhabi
    Edge(104, 102, distance_m=1200, has_stairs=False, nature_score=1.0, car_allowed=True, base_speed_kmh=60),
    
    # 4. Abu Dhabi to Triumphal Arch (Mangilik El)
    Edge(102, 103, distance_m=2000, has_stairs=False, nature_score=1.0, car_allowed=True, base_speed_kmh=60),
    
    # 5. Triumphal Arch to Expo
    Edge(103, 2, distance_m=1500, has_stairs=False, nature_score=2.0, car_allowed=True, base_speed_kmh=60),
    
    # 6. Abu Dhabi to Khan Shatyr (cross path)
    Edge(102, 3, distance_m=2800, has_stairs=False, nature_score=2.0, car_allowed=True, base_speed_kmh=50),
    
    # 7. Botanical Garden paths (NO CARS, HIGH NATURE)
    Edge(102, 101, distance_m=900, has_stairs=False, nature_score=10.0, car_allowed=False, base_speed_kmh=5),
    Edge(3, 101, distance_m=1500, has_stairs=False, nature_score=9.0, car_allowed=False, base_speed_kmh=5),
    Edge(101, 2, distance_m=2000, has_stairs=False, nature_score=10.0, car_allowed=False, base_speed_kmh=5),
]

EDGES = []
for e in _RAW_EDGES:
    # Adding both directions
    EDGES.append(e)
    EDGES.append(Edge(e.target, e.source, e.distance_m, e.has_stairs, e.nature_score, e.car_allowed, e.base_speed_kmh))

class RoutingEngine:
    def __init__(self):
        self.adj = {n: [] for n in NODES}
        for e in EDGES:
            self.adj[e.source].append(e)

    def calculate_route(self, start_id: int, end_id: int, mode: str, traffic_congestion_map: Dict[int, float] = None) -> Dict:
        """
        mode: "car_fast" (тез/машинамен), "pedestrian" (жаяу), "barrier_free" (кедергісіз), "anti_stress" (антистресс)
        traffic_congestion_map: Dict of node_id -> congestion level (0.0=free, 100.0=completely blocked) 
                                (This acts as the AI boltjam factor)
        Returns: { 'path': [...nodes], 'total_cost': ..., 'distance_m': ..., 'travel_time_sec': ... }
        """
        if start_id not in NODES or end_id not in NODES:
            return {"error": "Invalid start or end node"}
            
        traffic_map = traffic_congestion_map or {}

        # Priority queue: (cost, current_node, path, distance_acc, time_acc)
        pq = [(0.0, start_id, [start_id], 0.0, 0.0)]
        visited = set()
        
        while pq:
            cost, u, path, dist, time_sec = heapq.heappop(pq)
            
            if u == end_id:
                return {
                    "path": [NODES[n].__dict__ for n in path],
                    "total_cost_metric": round(cost, 2),
                    "total_distance_m": round(dist, 1),
                    "estimated_time_min": round(time_sec / 60.0, 1),
                    "mode_used": mode
                }
                
            if u in visited:
                continue
            visited.add(u)
            
            # AI Traffic penalty at node `u`. If it's blocked, it affects roads starting from here.
            # Convert 0-100 to a delay factor (1.0 = normal, 5.0 = huge jam)
            traffic_penalty = 1.0 + (traffic_map.get(u, 0.0) / 100.0) * 4.0
            
            for edge in self.adj[u]:
                v = edge.target
                edge_cost = 0.0
                edge_time = 0.0
                
                if mode == "car_fast":
                    if not edge.car_allowed:
                        continue # can't drive here
                    # Speed is reduced by traffic penalty
                    actual_speed_kmh = edge.base_speed_kmh / traffic_penalty
                    # Time in seconds
                    edge_time = (edge.distance_m / 1000.0) / actual_speed_kmh * 3600
                    # Cost is purely time
                    edge_cost = edge_time
                    
                elif mode == "pedestrian":
                    # Walking speed ~ 5 km/h
                    # Not affected by car traffic directly
                    edge_time = (edge.distance_m / 1000.0) / 5.0 * 3600
                    edge_cost = edge_time
                    
                elif mode == "barrier_free":
                    edge_time = (edge.distance_m / 1000.0) / 4.0 * 3600 # Slightly slower
                    edge_cost = edge_time
                    if edge.has_stairs:
                        # Massive penalty to effectively disable this route
                        edge_cost += 9999999.0
                        
                elif mode == "anti_stress":
                    # For pedestrians. Optimize for nature, avoid stairs and high traffic
                    edge_time = (edge.distance_m / 1000.0) / 4.0 * 3600
                    # Base cost is time
                    edge_cost = edge_time 
                    
                    # Reward nature (subtract cost or add penalty for low nature)
                    # nature_score is 0-10. So 10 - nature_score is a penalty.
                    nature_penalty = (10.0 - edge.nature_score) * 100.0
                    edge_cost += nature_penalty
                    
                    if edge.has_stairs:
                        edge_cost += 500.0 # moderate penalty stringency
                        
                    # Also penalize walking next to heavy traffic
                    if traffic_penalty > 2.0:
                        edge_cost += 500.0 * traffic_penalty

                heapq.heappush(pq, (cost + edge_cost, v, path + [v], dist + edge.distance_m, time_sec + edge_time))
                
        return {"error": "No path found"}

routing_engine = RoutingEngine()
