# backend/app/services/simulation_service.py
"""
Сервис для управления симуляцией трафика.
Хранит глобальный объект TrafficSimulator.
"""
from app.simulate import TrafficSimulator
from app.core.config import settings

# Глобальный объект симулятора
sim = TrafficSimulator(settings.db_path)
