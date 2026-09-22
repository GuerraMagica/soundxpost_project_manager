from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.config import settings
from app.database import Base, engine
from app.routers import (
    activity,
    adr,
    archive,
    auth,
    dashboard,
    delivery,
    episodes,
    projects,
    risks,
    tasks,
    users,
)

# MVP bootstrap: tables are created directly. Alembic migrations (see
# backend/alembic) are the source of truth once the schema stabilizes /
# on the PostgreSQL migration path.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Virtual Postproduction Coordinator — API de negocio (MVP local, SQLite).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(episodes.router)
app.include_router(tasks.router)
app.include_router(adr.router)
app.include_router(delivery.router)
app.include_router(archive.router)
app.include_router(risks.router)
app.include_router(activity.router)
app.include_router(users.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}
