import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.routes import router as api_router
from app.api.websocket import ws_router
from app.api.views import views_router

def create_app() -> FastAPI:
    """Application factory for CortxOS Multi-Agent Studio runtime."""
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Mount API routes, WebSocket handlers, and Shell views
    application.include_router(api_router)
    application.include_router(ws_router)
    application.include_router(views_router)

    # Mount static assets directory
    application.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

    return application

app = create_app()
