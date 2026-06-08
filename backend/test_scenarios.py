import os
import pytest
import httpx
import asyncio

BASE_URL = os.getenv("BASE_URL", "https://ai-traffics.onrender.com")

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

@pytest.fixture(scope="module")
def shared_data():
    return {"start_node": None, "end_node": None, "base_time": 0}

async def test_routing_nodes(shared_data):
    """[1] Получение узлов для маршрутизации"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"{BASE_URL}/routes/nodes")
        assert response.status_code == 200, "Failed to get nodes"
        
        nodes = response.json().get("nodes", [])
        assert len(nodes) > 0, "No nodes returned"
        
        start_node_data = next((n for n in nodes if "Байтерек" in n["name"]), nodes[0])
        end_node_data = next((n for n in nodes if "Экспо" in n["name"]), nodes[-1])
        
        shared_data["start_node"] = start_node_data["node_id"]
        shared_data["end_node"] = end_node_data["node_id"]
        shared_data["start_node_lat"] = start_node_data["lat"]
        shared_data["start_node_lon"] = start_node_data["lon"]

async def test_routing_modes(shared_data):
    """[2] Сравнение 4 режимов маршрутизации (TC-08 - TC-10)"""
    start_node = shared_data.get("start_node")
    end_node = shared_data.get("end_node")
    assert start_node and end_node, "Nodes not initialized"

    modes = ["car_fast", "pedestrian", "barrier_free", "anti_stress"]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for mode in modes:
            payload = {
                "start_node_id": start_node,
                "end_node_id": end_node,
                "mode": mode
            }
            resp = await client.post(f"{BASE_URL}/routes/calculate", json=payload)
            assert resp.status_code == 200, f"Failed for mode {mode}"
            
            data = resp.json()
            assert "total_distance_m" in data
            assert "estimated_time_min" in data
            
            if mode == "car_fast":
                shared_data["base_time"] = data["estimated_time_min"]

async def test_digital_twin_simulation(shared_data):
    """[3] Симуляция Digital Twin (TC-11 - TC-12)"""
    start_node = shared_data.get("start_node")
    end_node = shared_data.get("end_node")
    base_time = shared_data.get("base_time")
    
    assert start_node and end_node, "Nodes not initialized"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Создаем инцидент
        closure_payload = {
            "lat": shared_data["start_node_lat"],
            "lon": shared_data["start_node_lon"],
            "duration_min": 15
        }
        resp = await client.post(f"{BASE_URL}/traffic/simulate_closure", json=closure_payload)
        assert resp.status_code == 200, "Failed to simulate closure"
        
        # Даем системе время обновиться (если нужно)
        await asyncio.sleep(2)
        
        # Пересчитываем маршрут
        recalc_payload = {
            "start_node_id": start_node,
            "end_node_id": end_node,
            "mode": "car_fast"
        }
        recalc_resp = await client.post(f"{BASE_URL}/routes/calculate", json=recalc_payload)
        assert recalc_resp.status_code == 200, "Failed to recalculate route"
        
        new_data = recalc_resp.json()
        new_time = new_data['estimated_time_min']
        
        # Инцидент должен увеличить или оставить время неизменным (зависит от других путей)
        assert new_time >= base_time, "Time should increase or stay same after closure"
