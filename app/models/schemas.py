from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple

class Person(BaseModel):
    lat: float = Field(..., description="Широта")
    lon: float = Field(..., description="Долгота")

class MultiRequest(BaseModel):
    people: List[Person] = Field(..., min_items=2, description="Список участников (>=2)")
    # В API принудительно используем public_transport + reverse=False,
    # но поля оставим для совместимости и будущей эволюции
    transport: str = Field("public_transport", description="walking|driving|bicycle|public_transport")
    reverse: bool = Field(False, description="False: от точки; True: к точке (не для public_transport)")
    start_time_iso: Optional[str] = Field(None, description="RFC3339, напр. 2025-10-04T10:00:00Z")
    detailing: Optional[float] = Field(None, description="0..1, детализация полигона")
    t_start_min: int = Field(20, ge=1, description="Минимальное время (мин)")
    t_end_min: int = Field(40, gt=0, description="Максимальное время (мин)")
    t_step_min: int = Field(10, gt=0, description="Шаг (мин)")
    tolerance_min: int = Field(10, ge=0, description="Допуск |Δt| (мин)")

class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]

class MultiRequestByAddress(BaseModel):
    addresses: List[str] = Field(..., min_items=2, description="Список адресных строк (>=2)")
    # Необязательные хинты для геокодера — повышают точность (см. оф. док)
    city_id: Optional[str] = Field(None, description="Идентификатор города (часть id до подчёркивания из ответа /geocode)")
    location: Optional[Tuple[float, float]] = Field(None, description="(lon, lat): точка для сортировки по distance")
    # Параметры изохрон остаются теми же:
    start_time_iso: Optional[str] = Field(None, description="RFC3339")
    detailing: Optional[float] = Field(None, description="0..1")
    tolerance_min: int = Field(5, ge=0, description="Допуск |Δt| (мин)")