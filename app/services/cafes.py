from typing import Any, Dict, List, Optional, Set, Tuple
from ..clients.dgis import call_places_polygon, item_to_feature
from ..geometry.ops import explode_polygons

def search_cafes_in_geometry(geom) -> Dict[str, Any]:
    polygons = explode_polygons(geom)
    if not polygons:
        return {"type": "FeatureCollection", "features": []}

    seen_ids: Set[str] = set()
    out_features: List[Dict[str, Any]] = []

    for poly in polygons:
        polygon_wkt = poly.wkt
        items = call_places_polygon(polygon_wkt=polygon_wkt, q="cafe", page_size=50, max_pages=40)
        for it in items:
            it_id = it.get("id")
            if not it_id or it_id in seen_ids:
                continue
            feat = item_to_feature(it)
            if not feat:
                continue
            seen_ids.add(it_id)
            out_features.append(feat)

    return {"type": "FeatureCollection", "features": out_features}