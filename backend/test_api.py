import pytest
import httpx

# Тестируем живой облачный сервер
BASE_URL = "https://ai-traffics.onrender.com"

@pytest.mark.asyncio
async def test_cloud_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health", timeout=30.0)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_cloud_locations():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/locations", timeout=30.0)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0

@pytest.mark.asyncio
async def test_cloud_traffic_map():
    async with httpx.AsyncClient() as client:
        # Проверяем горизонт 30 минут
        response = await client.get(f"{BASE_URL}/traffic/map?horizon=30", timeout=30.0)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        # Проверяем структуру сегмента
        if len(data["items"]) > 0:
            assert "value" in data["items"][0]

@pytest.mark.asyncio
async def test_cloud_recommendation():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/traffic/recommendation", timeout=30.0)
        assert response.status_code == 200
        assert "message" in response.json()
