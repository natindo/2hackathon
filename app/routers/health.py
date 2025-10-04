from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {
        "ok": True,
        "post_example_multi": {
            "endpoint": "/equal-time-area/multi",
            "method": "POST",
            "body": {
                "people": [
                    {"lat": 55.75, "lon": 37.62},
                    {"lat": 55.70, "lon": 37.60},
                    {"lat": 55.73, "lon": 37.65}
                ],
                "tolerance_min": 5,
                "start_time_iso": None,
                "detailing": None
            },
            "notes": "Транспорт всегда public_transport, reverse всегда False. Первый поиск 20 минут, затем +10, пока не найдём или не упрёмся в потолок."
        }
    }