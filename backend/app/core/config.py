import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Делаем путь абсолютным относительно корня backend
    db_path: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "traffic.db"))
    data_mode: str = "SIM"
    seed: int = 42
    admin_login: str
    admin_password: str
    
    supabase_url: str = "https://nxmefixitnmfzgaxlzsl.supabase.co"
    supabase_key: str = ""

    # Multimodal coefficients
    multimodal_car_ratio: float = 0.6
    multimodal_scooter_ratio: float = 0.4
    multimodal_car_speed_ms: float = 8.33
    multimodal_scooter_speed_ms: float = 4.0
    multimodal_transfer_time_sec: int = 180
    multimodal_scooter_only_dist_m: int = 2000

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")

settings = Settings()
# Убедимся, что папка data существует
os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)
