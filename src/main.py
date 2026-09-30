from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

from database import create_db_and_tables
from routers import projects

# 💡 The modern way to handle setup and cleanup logic in FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Create tables in your PostgreSQL database
    create_db_and_tables()
    yield
    # Shutdown: Clean up operations go here if needed (e.g. closing connection pools)

app = FastAPI(lifespan=lifespan)

# Register the modular router
app.include_router(projects.router)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok", "message": "MedBlue-Data Successfully Deployed"}

