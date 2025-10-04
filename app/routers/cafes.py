from fastapi import APIRouter, HTTPException
from typing import List, Tuple
from ..models.schemas import MultiRequest
from ..services.isochrone import compute_intersection_iterative
from ..services.cafes import search_cafes_in_geometry

router = APIRouter(prefix="/cafes", tags=["cafes"])

@router.post("/multi")
def cafes_multi(req: MultiRequest):
    if len(req.people) < 2:
        raise HTTPException(status_code=400, detail="Нужно минимум 2 участника.")
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

    return search_cafes_in_geometry(inter)