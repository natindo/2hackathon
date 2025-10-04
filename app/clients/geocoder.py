# app/clients/geocoder.py
from typing import Any, Dict, Optional, Tuple
import requests
from fastapi import HTTPException

from ..core.config import get_settings
from ..core.http import get_session

_settings = get_settings()
_session = get_session()

def geocode_one(
    query: str,
    *,
    location: Optional[Tuple[float, float]] = None,  # (lon, lat) — для сортировки по расстоянию
    city_id: Optional[str] = None,
    page_size: int = 1
) -> Tuple[float, float]:
    """
    Прямое геокодирование строки адреса в (lat, lon).
    Использует /3.0/items/geocode с полями items.point.
    Если ничего не найдено — HTTP 404.
    """
    params: Dict[str, Any] = {
        "key": _settings.DGIS_API_KEY,
        "fields": "items.point,items.full_name",
        "page_size": page_size,
    }

    # Режимы запроса (см. оф. примеры 2ГИС Geocoder)
    # q — строка адреса; city_id — для жёсткого таргетинга города; location — хинт, чтобы сортировать ближе.
    if query:
        params["q"] = query
    if city_id:
        params["city_id"] = city_id
    if location:
        lon, lat = location
        params["location"] = f"{lon},{lat}"
        params["sort"] = "distance"

    try:
        resp = _session.get("https://catalog.api.2gis.com/3.0/items/geocode", params=params, timeout=_settings.HTTP_TIMEOUT_SEC)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"2ГИС Geocoder error: {e}") from e

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"2ГИС Geocoder HTTP {resp.status_code}: {resp.text}")

    data = resp.json() or {}
    result = data.get("result") or {}
    items = result.get("items") or []
    if not items:
        raise HTTPException(status_code=404, detail=f"Адрес не найден: {query!r}")

    # Берём первый результат и его point
    best = items[0]
    point = (best.get("point") or {})
    lon = point.get("lon")
    lat = point.get("lat")
    if lon is None or lat is None:
        raise HTTPException(status_code=422, detail=f"Не удалось получить координаты для адреса: {query!r}")

    return (lat, lon)