from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.db import create_db_and_tables
from backend.routers import ai, categories, tasks

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="todo-reminder-ai", lifespan=lifespan)

app.include_router(tasks.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ai_enabled": bool(settings.anthropic_api_key),
    }


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
