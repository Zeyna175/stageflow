"""
Point d entree de l application StageFlow.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import applications, auth, offers, users
from app.core.config import get_settings
from app.core.errors import AppError

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API interne de gestion securisee des stages data.",
    version="0.1.0",
)


@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(offers.router)
app.include_router(applications.router)
