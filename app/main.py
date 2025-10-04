from fastapi import FastAPI
from .routers import health, equal_time, cafes

def create_app() -> FastAPI:
    app = FastAPI(title="Equal-Arrival-Time Area API (2GIS Isochrone)")
    app.include_router(health.router)
    app.include_router(equal_time.router)
    app.include_router(cafes.router)
    return app

app = create_app()