# app/services/geocode.py
from typing import List, Optional, Tuple
from fastapi import HTTPException
from ..clients.geocoder import geocode_one

def geocode_many(
    addresses: List[str],
    *,
    city_id: Optional[str] = None,
    location: Optional[Tuple[float, float]] = None
) -> List[Tuple[float, float]]:
    """
    Геокодирует список адресов в список (lat, lon).
    Бросает 400, если список пуст; 404 — если какой-то адрес не найден.
    """
    if not addresses:
        raise HTTPException(status_code=400, detail="Список addresses пуст.")

    coords: List[Tuple[float, float]] = []
    for addr in addresses:
        lat, lon = geocode_one(addr, city_id=city_id, location=location)
        coords.append((lat, lon))
    return coords