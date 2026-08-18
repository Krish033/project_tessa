import os
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.pipeline.tools.meta.registry import ToolRegistry
from app.pipeline.tools.loader import load_tools
from app.pipeline.tools.meta.executor import ToolExecutor
from app.pipeline.llm import QwenLLM
from app.pipeline.context.manager import ContextManager
from app.agent import AgentLoop
from app.core.database import check_db_connection

# Initialize FastAPI App
app = FastAPI(
    title="Tessa AI Agent API",
    description="FastAPI service for Qwen/Ollama AI Agent with Gemini AI Online UI",
    version="1.0.0",
)

# Shared singletons
registry = ToolRegistry()
load_tools(registry)
executor = ToolExecutor(registry=registry)
llm = QwenLLM()
context_manager = ContextManager(llm=llm)

# Mount static files directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt or query for the AI agent")


@app.get("/")
async def get_index():
    """Serve the Gemini AI Online styled frontend interface."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "Gemini AI Agent API is running. static/index.html not found."})


@app.get("/api/health")
async def health_check():
    """Health check endpoint checking database and Ollama status."""
    db_ok = check_db_connection()
    ollama_ok = False
    try:
        res = llm.client.list()
        ollama_ok = True
    except Exception:
        ollama_ok = False

    return {
        "status": "healthy" if (db_ok or ollama_ok) else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "ollama": "online" if ollama_ok else "offline",
        "model": llm.model_name,
        "tools_count": len(registry.get_all()),
    }


@app.get("/api/tools")
async def list_tools():
    """List all registered tools available to the AI agent."""
    tools_list = registry.get_all()
    tools_data = [
        {"name": t.name, "description": t.description}
        for t in tools_list
    ]
    return {"tools": tools_data, "count": len(tools_data)}



@app.post("/api/chat")
async def chat_sync(req: ChatRequest):
    """Synchronous chat endpoint (returns full JSON response once agent finishes)."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    agent = AgentLoop(ctx=context_manager, llm=llm, executor=executor, verbose=True)
    try:
        answer = await agent.run(req.prompt)
        return {"status": "success", "prompt": req.prompt, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/stream")
async def chat_stream(prompt: str = Query(..., description="User prompt")):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Yields real-time events as data: JSON lines.
    """
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt query parameter required")

    agent = AgentLoop(ctx=context_manager, llm=llm, executor=executor, verbose=False)

    async def event_generator():
        try:
            async for event in agent.run_event_stream(prompt):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/chat/reset")
async def reset_chat():
    """Reset the context manager history for a new conversation."""
    global context_manager
    context_manager = ContextManager(llm=llm)
    return {"status": "success", "message": "Chat history cleared"}
