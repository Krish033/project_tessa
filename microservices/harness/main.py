import sys
from pathlib import Path

# Ensure root directory is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from contextlib import asynccontextmanager, suppress
from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from microservices.harness.app.context.manager import ContextManager
from microservices.harness.app.loop import AgentLoop, DEFAULT_FALLBACK_ANSWER
from microservices.harness.app.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    ExecuteToolRequest,
    ExecuteToolResponse,
    ToolInfoResponse,
    ToolListResponse,
)
from microservices.harness.app.tools.executor import ToolExecutor
from microservices.harness.app.tools.loader import load_tools
from microservices.harness.app.tools.policies.permission_manager import PermissionManager
from microservices.harness.app.tools.policies.safety_policy import SafetyPolicy
from microservices.harness.app.tools.registry import ToolRegistry
from shared.config.config import settings
from shared.config.logging import configure_logging, get_logger
from shared.rabbitmq import get_rabbitmq

logger = get_logger(__name__)

# Service singletons
registry = ToolRegistry()
permission_manager = PermissionManager()
safety_policy = SafetyPolicy()
executor = ToolExecutor(
    registry=registry,
    permission_manager=permission_manager,
    safety_policy=safety_policy,
)


# ── Core Agent Runner Logic ──────────────────────────────────────────

async def execute_agent_job(payload_data: dict[str, Any]) -> dict[str, Any]:
    """Execute the harness agent loop for a prompt.

    Data/conversations remain owned by Gateway.
    """
    prompt = payload_data.get("prompt", "")
    conversation_id = payload_data.get("conversation_id")
    history = payload_data.get("history") or []
    max_iterations = payload_data.get("max_iterations", 10)

    context_manager = ContextManager(conversation_id=conversation_id)

    # Populate context with history sent from Gateway
    for item in history:
        context_manager.ctx.append({
            "id": item.get("id", ""),
            "role": item.get("role", "user"),
            "content": item.get("content", ""),
        })

    agent = AgentLoop(
        ctx=context_manager,
        llm=None,  # LLM step intentionally deferred
        executor=executor,
        max_iterations=max_iterations,
        verbose=settings.debug,
    )

    answer = await agent.run(prompt)

    return {
        "status": "success",
        "conversation_id": conversation_id,
        "answer": answer,
        "iterations": 1,
        "tool_calls": [],
    }


async def execute_tool_job(payload_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a single tool via registry & policy executor."""
    tool_name = payload_data.get("tool_name", "")
    arguments = payload_data.get("arguments", {})
    result = await executor.execute(tool_name, arguments)
    return {
        "tool": tool_name,
        "success": result.get("success", True),
        "result": result.get("result", result),
    }


def get_registered_tools_info() -> list[dict[str, Any]]:
    """Return tool catalog."""
    tools = registry.get_all()
    return [
        {
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters,
            "risk": t.safety.risk.name if hasattr(t.safety.risk, "name") else str(t.safety.risk),
            "permission": t.safety.permission.name if hasattr(t.safety.permission, "name") else str(t.safety.permission),
        }
        for t in tools
    ]


async def list_tools_job(_d: dict[str, Any]) -> dict[str, Any]:
    return {"tools": get_registered_tools_info()}


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(debug=settings.debug)
    logger.info(f"Starting Harness Microservice on port {settings.harness_port}...")

    # Load tool definitions into registry
    load_tools(registry, sync_db=False)
    logger.info(f"Loaded {len(registry.get_all())} tools into ToolRegistry")

    # Connect to RabbitMQ and register RPC handlers for inter-service communication
    rabbit = get_rabbitmq()
    try:
        await rabbit.connect("harness")
        logger.info("RabbitMQ connected for harness")

        # Register RPC handlers
        await rabbit.register_rpc("harness.agent_run", execute_agent_job)
        await rabbit.register_rpc("harness.execute_tool", execute_tool_job)
        await rabbit.register_rpc("harness.list_tools", list_tools_job)
        logger.info("RabbitMQ RPC methods registered: harness.agent_run, harness.execute_tool, harness.list_tools")

    except Exception as err:
        logger.warning("rabbitmq_init_warning", error=str(err))

    yield

    logger.info("Shutting down Harness Service...")
    with suppress(Exception):
        await rabbit.disconnect()
    logger.info("Harness shutdown complete")


app = FastAPI(
    title="Tessa Agent Harness",
    description="Tool Execution, Policy Enforcement, and Agent Harness Loop Service (RabbitMQ-driven)",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1", tags=["agent"])


@app.get("/health", tags=["health"])
async def health_check():
    rabbit = get_rabbitmq()
    return {
        "status": "healthy",
        "service": "harness",
        "port": settings.harness_port,
        "tools_registered": len(registry.get_all()),
        "rabbitmq_connected": rabbit.is_connected,
    }


# Optional direct fallback HTTP endpoints that use the same core job functions
@router.post("/agent/run", response_model=AgentRunResponse, summary="Execute Agent Loop (HTTP Fallback)")
async def run_agent(payload: AgentRunRequest):
    try:
        result = await execute_agent_job(payload.model_dump())
        return AgentRunResponse(**result)
    except Exception as exc:
        logger.error("agent_run_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {exc}",
        )


@router.get("/tools", response_model=ToolListResponse, summary="List Registered Tools (HTTP Fallback)")
async def list_tools():
    return ToolListResponse(tools=[ToolInfoResponse(**t) for t in get_registered_tools_info()])


@router.post("/tools/execute", response_model=ExecuteToolResponse, summary="Execute Tool (HTTP Fallback)")
async def execute_tool(payload: ExecuteToolRequest):
    try:
        result = await execute_tool_job(payload.model_dump())
        return ExecuteToolResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "microservices.harness.main:app",
        host="0.0.0.0",
        port=settings.harness_port,
        reload=settings.debug,
    )
