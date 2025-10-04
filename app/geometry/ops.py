from typing import List, Dict, Any, Optional, Tuple
from shapely.geometry import mapping, Polygon, MultiPolygon
from shapely.ops import unary_union

def explode_polygons(geom) -> List[Polygon]:
    if geom is None:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    try:
        return [g for g in geom if isinstance(g, Polygon)]
    except TypeError:
        return []

def to_feature_collection(geom, props: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if geom is None or geom.is_empty:
        return {"type": "FeatureCollection", "features": []}
    if geom.geom_type == "Polygon":
        geoms = [geom]
    elif geom.geom_type == "MultiPolygon":
        geoms = list(geom.geoms)
    else:
        geoms = [g for g in geom if g.geom_type in ("Polygon", "MultiPolygon")]
    features = [{"type": "Feature", "properties": props or {}, "geometry": mapping(g)} for g in geoms]
    return {"type": "FeatureCollection", "features": features}

def chunked(iterable, size: int):
    it = list(iterable)
    for i in range(0, len(it), size):
        yield it[i : i + size]