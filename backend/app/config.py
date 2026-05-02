from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "SmartBalance"
    app_version: str = "1.0.0"
    database_url: str = "sqlite+aiosqlite:///./smartbalance.db"
    health_check_interval: float = 5.0
    health_check_failure_threshold: int = 3
    websocket_update_interval: float = 1.0
    lstm_model_path: str = "app/ml/trained_model.pt"
    lstm_window_size: int = 60
    lstm_forecast_steps: int = 15
    smart_router_threshold: float = 1.5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
