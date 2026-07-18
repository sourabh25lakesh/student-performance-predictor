"""
Student Performance Predictor — FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload

Swagger docs available at /docs, ReDoc at /redoc.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api import auth, dashboard, predictions, users
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.database.database import init_db
from app.ml.model import load_model

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "A production-ready web application that predicts a student's final "
        "marks using a trained Linear Regression model, with full JWT "
        "authentication and MySQL-backed prediction history."
    ),
    version="1.0.0",
)

# ----------------------------------------------------------------------
# CORS
# ----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# Routers
# ----------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(predictions.router)
app.include_router(dashboard.router)


# ----------------------------------------------------------------------
# Error handling
# ----------------------------------------------------------------------
@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database error while handling %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."},
    )


# ----------------------------------------------------------------------
# Startup
# ----------------------------------------------------------------------
@app.on_event("startup")
def on_startup() -> None:
    logger.info("Starting %s (environment=%s)...", settings.PROJECT_NAME, settings.ENVIRONMENT)
    init_db()
    load_model()


# ----------------------------------------------------------------------
# Health check
# ----------------------------------------------------------------------
@app.get("/", tags=["Health"], summary="Health check")
def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
