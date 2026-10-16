from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.incidents import router as incidents_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401 - register SQLAlchemy models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Starter-only convenience. Use Alembic migrations for shared/production environments.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(incidents_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "garage-aiops-api", "version": "0.1.0"}
