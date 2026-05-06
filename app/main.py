from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.models import user  # noqa: F401  (import necesario para registrar el modelo)
from app.routes import auth, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas si no existen al arrancar la app
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description="REST API for task management with JWT authentication",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(auth.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
    }