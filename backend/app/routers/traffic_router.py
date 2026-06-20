# backend/app/routers/traffic_router.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
import time

from app.core.database import get_conn_dep
from app.services.ml_service import get_traffic_recommendation, get_model_metrics
from app.services.routing_service import multimodal_analysis
from app.services.simulation_service import sim
from app.models.schemas import SimulationRequest, MultimodalRequest
from app.repositories.traffic_repository import get_locations, get_road_segments
from app.vehicles import veh_sim
from app.weather import weather_service

router = APIRouter(tags=["traffic"])

@router.get("/weather")
async def get_weather():
    return await weather_service.get_current_weather()

@router.get("/locations")
def api_get_locations(conn=Depends(get_conn_dep)):
    return {"items": get_locations(conn)}

@router.get("/road_segments")
def api_get_road_segments(location_id: Optional[int] = None, conn=Depends(get_conn_dep)):
    return {"items": get_road_segments(conn, location_id)}

@router.get("/traffic/recommendation")
async def api_traffic_recommendation(location_id: int = Query(None), conn=Depends(get_conn_dep)):
    return await get_traffic_recommendation(conn, location_id)

@router.get("/model_metrics")
def api_model_metrics(horizon: int, conn=Depends(get_conn_dep)):
    return get_model_metrics(conn, horizon)

@router.post("/traffic/simulate_closure")
def api_simulate_closure(req: SimulationRequest):
    sim.add_custom_hotspot(req.lat, req.lon, strength=95.0, radius_deg=0.012, ttl_seconds=req.duration_min * 60)
    return {
        "status": "success",
        "message": f"Очаг пробки успешно создан. Действует {req.duration_min} мин."
    }

@router.post("/traffic/multimodal_analysis")
async def api_multimodal_analysis(req: MultimodalRequest):
    return multimodal_analysis(req.duration_now_sec, req.distance_meters)

@router.get("/smart_alert")
async def get_smart_alert():
    weather = await weather_service.get_current_weather()
    items = sim.snapshot(30)
    avg_future_traffic = 0.0
    if items:
        avg_future_traffic = sum(it.get('value', 0.0) for it in items) / len(items)
        
    wf = weather.get('traffic_factor', 1.0)
    
    if wf > 1.3 or avg_future_traffic > 70:
        return {
            "has_alert": True,
            "title": "Умное предупреждение 🚨",
            "body": f"Ожидаются сильные пробки из-за плохих погодных условий ({weather['description']}). Рекомендуем выехать на 15 минут раньше!"
        }
    elif wf > 1.1 or avg_future_traffic > 50:
        return {
            "has_alert": True,
            "title": "Внимание на дорогах ⚠️",
            "body": f"Трафик начинает уплотняться ({weather['description']}). Планируйте маршрут заранее."
        }
        
    return {
        "has_alert": True,
        "title": "Дороги свободны 🟢",
        "body": "Сейчас отличное время для поездки. Погода благоприятная!"
    }

@router.get("/vehicles")
def get_vehicles():
    return {"items": veh_sim.snapshot()}

# --- Simulation control endpoints ---
@router.post("/simulate/start")
def start_sim():
    sim.start()
    veh_sim.start()
    return {"status": "started"}

@router.post("/simulate/stop")
def stop_sim():
    sim.stop()
    veh_sim.stop()
    return {"status": "stopped"}

@router.get("/simulate/status")
def status_sim():
    return {"running": sim.is_running(), "hotspots": sim.hotspots_count()}

@router.get("/simulate/snapshot")
def snapshot_sim(horizon_min: int = 0):
    return {"items": sim.snapshot(horizon_min)}

@router.post("/simulate/hotspot")
def add_hotspot(req: SimulationRequest):
    sim.add_custom_hotspot(req.lat, req.lon, strength=80.0, radius_deg=0.015, ttl_seconds=req.duration_min * 60)
    return {"status": "hotspot added"}
