from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Base de dados
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/smart_campus"
    DB_ECHO: bool = False  # True em dev para ver SQL

    # Localização do campus (IPT — Tomar)
    CAMPUS_LATITUDE: float = 39.6036
    CAMPUS_LONGITUDE: float = -8.4133
    CAMPUS_MUNICIPIO: str = "tomar"

    # Limiares de alertas
    ALERT_TEMP_MAX: float = 30.0
    ALERT_TEMP_MIN: float = 16.0
    ALERT_CO2_MAX: int = 1000       # ppm
    ALERT_HUMIDITY_MAX: float = 80.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Instância global usada em todo o projeto
settings = get_settings()