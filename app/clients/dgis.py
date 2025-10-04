from typing import Any, Dict, List, Optional, Tuple
import requests
from shapely import wkt
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

from fastapi import HTTPException
from ..core.config import get_settings
from ..core.http import get_session
from ..core.errors import ExternalServiceError, IsochroneBuildError
from ..geometry.ops import chunked

_settings = get_settings()
_session = get_session()

def _items_fields() -> str:
    return ",".join([
        "items.point",
        "items.name",
        "items.rubrics",
        "items.schedule",
        "items.address",
        "items.rating",
        "items.contact_groups",
    ])

def call_isochrone(
    lat: float,
    lon: float,
    durations_sec: List[int],
    transport: str = "public_transport",
    reverse: bool = False,
    start_time_iso: Optional[str] = None,
    detailing: Optional[float] = None,
    max_durations_per_call: int = 5,
) -> List[Tuple[int, MultiPolygon | Polygon]]:
    params = {"key": _settings.DGIS_API_KEY}
    results_map: dict[int, MultiPolygon | Polygon] = {}

    def _call(batch, use_start_time=True, use_detailing=True) -> requests.Response:
        payload: Dict[str, Any] = {
            "durations": batch,
            "start": {"lat": lat, "lon": lon},
            "transport": transport,
            "reverse": reverse,
            "format": "wkt",
        }
        if use_start_time and start_time_iso:
            payload["start_time"] = start_time_iso
        if use_detailing and (detailing is not None):
            payload["detailing"] = float(detailing)

        return _session.post(
            str(_settings.ISOCHRONE_URL),
            params=params,
            json=payload,
            timeout=_settings.HTTP_TIMEOUT_SEC,
        )

    # батчим запросы по <=5 durations
    for batch in chunked(sorted(set(durations_sec)), max_durations_per_call):
        resp = _call(batch, use_start_time=True, use_detailing=True)
        if resp.status_code != 200:
            raise ExternalServiceError(f"Isochrone API HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        if data.get("status") != "OK" or "isochrones" not in data:
            raise IsochroneBuildError(str(data))

        for item in data["isochrones"]:
            geom_wkt = item.get("geometry")
            duration = int(item.get("duration"))
            if not geom_wkt:
                continue
            geom = wkt.loads(geom_wkt)
            if duration in results_map:
                results_map[duration] = unary_union([results_map[duration], geom])
            else:
                results_map[duration] = geom

    if not results_map:
        raise IsochroneBuildError(
            "Сервис не вернул ни одной изохроны. Проверьте координаты/транспорт/время."
        )

    return sorted(results_map.items(), key=lambda x: x[0])

def call_places_polygon(
    polygon_wkt: str,
    q: str = "cafe",
    page_size: int = 50,
    max_pages: int = 40,
) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    page = 1
    while page <= max_pages:
        params = {
            "key": _settings.DGIS_API_KEY,
            "q": q,
            "type": "branch",
            "polygon": polygon_wkt,
            "fields": _items_fields(),
            "page_size": page_size,
            "page": page,
        }
        try:
            resp = _session.get(
                str(_settings.PLACES_ITEMS_URL),
                params=params,
                timeout=_settings.HTTP_TIMEOUT_SEC,
            )
        except requests.RequestException as e:
            raise ExternalServiceError(f"2ГИС Places error: {e}") from e

        if resp.status_code != 200:
            raise ExternalServiceError(f"2ГИС Places HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        result = data.get("result") or {}
        page_items = result.get("items") or []
        if not page_items:
            break

        items.extend(page_items)
        if len(page_items) < page_size:
            break
        page += 1

    return items

def item_to_feature(it: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pt = (it.get("point") or {})
    lon = pt.get("lon")
    lat = pt.get("lat")
    if lon is None or lat is None:
        return None

    props: Dict[str, Any] = {
        "source": "2GIS Places",
        "dgis_id": it.get("id"),
        "name": it.get("name"),
        "address": it.get("address"),
        "rating": (it.get("rating") or {}).get("rating"),
        "rating_count": (it.get("rating") or {}).get("reviews"),
        "rubrics": [r.get("name") for r in (it.get("rubrics") or []) if r.get("name")],
        "phones": [],
        "websites": [],
    }

    for cg in it.get("contact_groups") or []:
        for c in cg.get("contacts") or []:
            ctype = c.get("type")
            if ctype == "phone":
                number = c.get("value")
                if number:
                    props["phones"].append(number)
            elif ctype == "website":
                url = c.get("value")
                if url:
                    props["websites"].append(url)

    return {"type": "Feature", "properties": props, "geometry": {"type": "Point", "coordinates": [lon, lat]}}