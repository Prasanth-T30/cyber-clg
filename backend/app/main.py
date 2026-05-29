"""
FusionGuardNet – FastAPI Application Entry Point
"""

import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.sqlite_db import init_db
from app.api.routes import alerts, dashboard, detections, websocket, auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Advanced Multimodal Intrusion Detection Framework — "
        "CNN + LSTM + Random Forest pipeline with real-time WebSocket alerts."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,      prefix="/api/v1")
app.include_router(alerts.router,    prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(detections.router,prefix="/api/v1")
app.include_router(websocket.router)


@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("  %s v%s starting...", settings.APP_NAME, settings.APP_VERSION)
    logger.info("=" * 60)

    # Init SQLite DB
    init_db()

    # Pre-train / load ML models
    from app.ml.models import cnn_model, lstm_model, random_forest_model

    async def _load_models():
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, cnn_model.train_cnn)
        await loop.run_in_executor(None, lstm_model.train_lstm)
        await loop.run_in_executor(None, random_forest_model.train_rf)
        logger.info("All ML models ready ✓")

    from app.packet_sniffer.sniffer import run_sniffer
    asyncio.create_task(_load_models())
    asyncio.create_task(run_sniffer())
    logger.info(
        "Packet sniffer started (%s mode)",
        "SIMULATION" if settings.SNIFFER_SIMULATION_MODE else "LIVE",
    )


@app.on_event("shutdown")
async def shutdown():
    logger.info("%s shutting down.", settings.APP_NAME)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/", tags=["health"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "ws":   "ws://localhost:8000/ws/alerts",
    }
