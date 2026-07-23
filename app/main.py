"""
Point d'entree de l'application StageFlow.

Ce fichier sera complete etape par etape avec :
- les exception handlers (core/errors.py)
- les middlewares (request_id, security_headers)
- les routers (auth, users, offers, applications)
"""

from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API interne de gestion securisee des stages data.",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}
