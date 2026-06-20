# backend/app/services/routing_service.py
"""
Сервис для работы с маршрутизацией, A* алгоритмом и мультимодальным анализом.
"""
from fastapi import HTTPException
from app.routing import routing_engine, NODES
from app.services.simulation_service import sim
from app.core.config import settings

def calculate_multicriteria_route(start_node_id: int, end_node_id: int, mode: str, horizon_min: int):
    if start_node_id not in NODES or end_node_id not in NODES:
        raise HTTPException(status_code=400, detail="Invalid node IDs")
        
    traffic_map = {}
    if mode in ["car_fast", "anti_stress"] or horizon_min > 0:
        snap_h = 30 if 15 <= horizon_min <= 45 else (60 if horizon_min > 45 else 0)
        snapshot = sim.snapshot(snap_h)
        if snapshot:
            for item in snapshot:
                loc_id = item.get("location_id")
                if loc_id in NODES:
                    traffic_map[loc_id] = item.get("value", 0.0)

    res = routing_engine.calculate_route(start_node_id, end_node_id, mode, traffic_map)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
        
    return res

def get_routing_nodes():
    return {"nodes": [n.__dict__ for n in NODES.values()]}

def multimodal_analysis(duration_now_sec: int, distance_meters: int):
    t1 = duration_now_sec
    
    items = sim.snapshot(30)
    avg_future_traffic = 0.0
    if items:
        avg_future_traffic = sum(it.get('value', 0.0) for it in items) / len(items)
        
    traffic_multiplier = 1.0 + (avg_future_traffic / 100.0) * 0.5
    t2 = int(t1 * traffic_multiplier)
    
    car_distance = distance_meters * settings.multimodal_car_ratio
    scooter_distance = distance_meters * settings.multimodal_scooter_ratio
    
    car_time = car_distance / settings.multimodal_car_speed_ms
    scooter_time = scooter_distance / settings.multimodal_scooter_speed_ms
    
    t3 = int(car_time + scooter_time + settings.multimodal_transfer_time_sec)
    
    if distance_meters < settings.multimodal_scooter_only_dist_m:
        t3 = int(distance_meters / settings.multimodal_scooter_speed_ms)

    recommend = t3 < t2
    
    return {
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "recommend_transfer": recommend,
        "scooter_distance": int(scooter_distance),
        "message": f"С учетом будущего затора, комбинированный маршрут сэкономит {max(0, (t2 - t3)//60)} минут." if recommend else "Оставайтесь на текущем маршруте."
    }
