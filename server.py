"""
CortxOS Server Entry Point
Delegates directly to modular application package `app.main:app` for backward compatibility.
"""
import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print(f"[*] Starting CortxOS Multi-Agent Sandbox on http://{settings.host}:{settings.port}")
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
