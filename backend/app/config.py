from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_path: str = "data/traffic.db"
    data_mode: str = "SIM"  # SIM or API (API will be added later)
    seed: int = 42
    # Админ-панель: логин и пароль (по умолчанию admin / admin123)
    admin_login: str = "admin"
    admin_password: str = "admin123"

settings = Settings()
