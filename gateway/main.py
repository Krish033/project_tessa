"""Gateway Service: central API gateway on its configured port.

Current scope: RabbitMQ connection + authentication. Proxy routes come later.
"""

from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from gateway.app.api.routes.auth import router as auth_router
from shared.config.config import settings
from shared.config.logging import configure_logging, get_logger
from shared.rabbitmq import get_rabbitmq

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(debug=settings.debug)
    logger.info(f"Starting Gateway on port {settings.gateway_port}...")

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