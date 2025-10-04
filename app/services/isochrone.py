from typing import Any, Dict, List, Optional, Tuple
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

from ..core.config import get_settings
from ..clients.dgis import call_isochrone

_settings = get_settings()

def build_time_rings(isochrones: List[Tuple[int, MultiPolygon | Polygon]]) -> List[Tuple[Tuple[int, int], MultiPolygon | Polygon]]:
    rings: List[Tuple[Tuple[int, int], MultiPolygon | Polygon]] = []
    prev_geom = None
    prev_t = None
    for duration, geom in isochrones:
        cur_geom = geom
        if prev_geom is None:
            rings.append(((0, duration), cur_geom))
        else:
            diff = cur_geom.difference(prev_geom)
            if not diff.is_empty:
                rings.append(((prev_t, duration), diff))
        prev_geom = cur_geom
        prev_t = duration
    return rings

def union_of_close_time_rings(rings, target_mid_s: float, delta_s: float):
    candidates = []
    for (t0, t1), g in rings:
        t_mid = (t0 + t1) / 2
        if abs(t_mid - target_mid_s) <= delta_s:
            candidates.append(g)
    if not candidates:
        return None
    return unary_union(candidates)

def intersect_rings_for_many(
    rings_list: List[List[Tuple[Tuple[int, int], Any]]],
    delta_minutes: int,
    min_minutes: Optional[int],
    max_minutes: Optional[int],
):
    if not rings_list:
        return None
    ref = rings_list[0]
    others = rings_list[1:]
    delta_s = delta_minutes * 60
    result = None

    for (t0, t1), g_ref in ref:
        t_mid = (t0 + t1) / 2
        if min_minutes is not None and t_mid / 60 < min_minutes:
            continue
        if max_minutes is not None and t_mid / 60 > max_minutes:
            continue

        cur = g_ref
        empty = False
        for rings in others:
            union_close = union_of_close_time_rings(rings, t_mid, delta_s)
            if union_close is None:
                empty = True
                break
            cur = cur.intersection(union_close)
            if cur.is_empty:
                empty = True
                break
        if empty or cur.is_empty:
            continue
        result = cur if result is None else unary_union([result, cur])
    return result

def compute_intersection_iterative(
    people: List[Tuple[float, float]],
    start_minutes: int = 20,
    step_minutes: int = 10,
    tolerance_min: int = 10,
    start_time_iso: Optional[str] = None,
    detailing: Optional[float] = None,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    transport = "public_transport"
    reverse = False
    debug = {"transport": transport, "reverse": reverse, "attempts": []}
    current_t = start_minutes

    while current_t <= _settings.MAX_MINUTES_CAP:
        durations = [current_t * 60]
        attempt_info = {"t_minutes": current_t, "durations_sec": durations}
        debug["attempts"].append(attempt_info)

        rings_list: List[List[Tuple[Tuple[int, int], Any]]] = []
        for (lat, lon) in people:
            iso = call_isochrone(
                lat=lat,
                lon=lon,
                durations_sec=durations,
                transport=transport,
                reverse=reverse,
                start_time_iso=start_time_iso,
                detailing=detailing,
            )
            rings = build_time_rings(iso)
            rings_list.append(rings)

        inter = intersect_rings_for_many(
            rings_list,
            delta_minutes=tolerance_min,
            min_minutes=None,
            max_minutes=None,
        )

        if inter is not None and (not inter.is_empty):
            attempt_info["status"] = "intersection_found"
            return inter, debug

        attempt_info["status"] = "no_intersection_retry"
        current_t += step_minutes

    return None, debug