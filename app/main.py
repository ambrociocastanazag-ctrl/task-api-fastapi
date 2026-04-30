"""Task API — FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="Task API",
    description="REST API for task management — built with FastAPI, PostgreSQL and SQLAlchemy.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health_check():
    """Liveness probe — returns 200 if the service is running."""
    return {"status": "ok"}


# Routers will be registered here on day 2:
# from app.routes import tasks
# app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
