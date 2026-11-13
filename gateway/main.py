"""Gateway Service: central API gateway on its configured port.

Current scope: RabbitMQ connection + authentication. Proxy routes come later.
"""

import sys
from pathlib import Path

# Ensure root and gateway directories are in python path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
GATEWAY_DIR = Path(__file__).resolve().parent
if str(GATEWAY_DIR) not in sys.path:
    sys.path.insert(0, str(GATEWAY_DIR))

from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.chats import router as chats_router
from app.api.routes.projects import router as projects_router
from app.api.routes.settings import router as settings_router
from shared.config.config import settings
from shared.config.logging import configure_logging, get_logger
from shared.rabbitmq import get_rabbitmq
from shared.config.database import engine, Base

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(debug=settings.debug)
    logger.info(f"Starting Gateway on port {settings.gateway_port}...")

    # Ensure tables exist in database
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified")
    except Exception as db_err:
        logger.warning("database_tables_init_warning", error=str(db_err))

    rabbit = get_rabbitmq()
    try:
        await rabbit.connect("gateway")
        logger.info("RabbitMQ connected for gateway")
    except Exception as err:
        logger.warning("rabbitmq_init_warning", error=str(err))

    yield

    logger.info("Shutting down Gateway...")
    with suppress(Exception):
        await rabbit.disconnect()
    logger.info("Gateway shutdown complete")


app = FastAPI(
    title="Signal Gateway",
    description="Central API Gateway",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chats_router, prefix="/api/v1/chats", tags=["chats"])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["settings"])

@app.get("/health", tags=["health"])
async def gateway_health():
    rabbit = get_rabbitmq()
    return {
        "status": "healthy",
        "gateway": {
            "port": settings.gateway_port,
            "rabbitmq_connected": rabbit.is_connected,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "gateway.main:app",
        host="0.0.0.0",
        port=settings.gateway_port,
        reload=settings.debug,
    )