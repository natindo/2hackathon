from fastapi import APIRouter, HTTPException
from typing import List, Tuple
from ..models.schemas import MultiRequest
from ..services.isochrone import compute_intersection_iterative
from ..geometry.ops import to_feature_collection

router = APIRouter(prefix="/equal-time-area", tags=["equal-time-area"])

@router.post("/multi")
def equal_time_area_multi(req: MultiRequest):
    if len(req.people) < 2:
        raise HTTPException(status_code=400, detail="Нужно минимум 2 участника.")

    # Принудительно используем PT + reverse=False
    people: List[Tuple[float, float]] = [(p.lat, p.lon) for p in req.people]

    inter, debug = compute_intersection_iterative(
        people=people,
        start_minutes=20,
        step_minutes=10,
        tolerance_min=req.tolerance_min,
        start_time_iso=req.start_time_iso,
        detailing=req.detailing,
    )

    if inter is None or inter.is_empty:
        raise HTTPException(
            status_code=404,
            detail={"message": "Не удалось найти общую область встречи для всех участников при допустимом времени.", "debug": debug},
        )

    fc = to_feature_collection(
        inter,
        {
            "source": "2GIS Isochrone",
            "participants": len(req.people),
            "transport": "public_transport",
            "reverse": False,
            "tolerance_min": req.tolerance_min,
            "attempts": debug["attempts"],
        },
    )
    return fc