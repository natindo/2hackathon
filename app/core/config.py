from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl
from typing import Optional

class Settings(BaseSettings):
    DGIS_API_KEY: str = Field(..., description="Ключ 2ГИС")
    ISOCHRONE_URL: AnyHttpUrl = Field("https://routing.api.2gis.com/isochrone/2.0.0")
    PLACES_ITEMS_URL: AnyHttpUrl = Field("https://catalog.api.2gis.com/3.0/items")

    HTTP_TIMEOUT_SEC: int = 30
    HTTP_RETRY_TOTAL: int = 3
    HTTP_RETRY_BACKOFF: float = 1  # секунды
    HTTP_POOL_SIZE: int = 10

    MAX_MINUTES_CAP: int = 40  # защитный потолок для итеративного поиска

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()