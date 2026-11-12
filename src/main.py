from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

from database import create_db_and_tables, seed_db
from routers import (projects, campaign_events, habitats, municipalities,
                     stations, station_geometries, sampling_events)


# 💡 The modern way to handle setup and cleanup logic in FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Create tables in your PostgreSQL database
    # create_db_and_tables()
    seed_db()
    yield
    # Shutdown: Clean up operations go here if needed (e.g. closing connection pools)

app = FastAPI(lifespan=lifespan)

# Register the modular router
app.include_router(projects.router)
app.include_router(campaign_events.router)
app.include_router(habitats.router)
app.include_router(municipalities.router)
app.include_router(stations.router)
app.include_router(station_geometries.router)
app.include_router(sampling_events.router)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok", "message": "MedBlue-Data Successfully Deployed"}

