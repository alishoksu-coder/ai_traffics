import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Делаем путь абсолютным относительно корня backend
    db_path: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "traffic.db"))
    data_mode: str = "SIM"
    seed: int = 42
    admin_login: str = "admin"
    admin_password: str = "admin123"

settings = Settings()
# Убедимся, что папка data существует
os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)
