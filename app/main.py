from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, equal_time, cafes

def create_app() -> FastAPI:
    app = FastAPI(title="Equal-Arrival-Time Area API (2GIS Isochrone)")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:63342"  # статичный хост
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(equal_time.router)
    app.include_router(cafes.router)
    return app

app = create_app()