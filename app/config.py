"""
Configurări aplicație
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/automotive_vest"

    # Application
    app_name: str = "Automotive Vest Analytics"
    app_version: str = "0.1.0"
    debug: bool = True

    # API
    api_prefix: str = "/api/v1"

    # Data settings
    data_start_year: int = 2010
    data_end_year: int = 2024

    # Regiuni și județe
    region_name: str = "Regiunea Vest"
    counties: list[str] = ["Timiș", "Arad", "Hunedoara", "Caraș-Severin"]
    county_codes: dict[str, str] = {
        "Timiș": "TM",
        "Arad": "AR",
        "Hunedoara": "HD",
        "Caraș-Severin": "CS"
    }

    # CAEN codes pentru automotive
    automotive_caen_codes: list[str] = [
        "2910",  # Fabricarea autovehiculelor
        "2920",  # Producția de caroserii
        "2931",  # Echipamente electrice și electronice
        "2932",  # Alte componente și accesorii
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
