from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Request payload to execute the autonomous agent loop."""
    prompt: str = Field(..., description="User prompt or task for the agent to execute")
    conversation_id: Optional[str] = Field(None, description="Optional conversation UUID reference")
    history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Optional prior conversation messages [{'role': 'user'|'assistant', 'content': '...'}] provided by Gateway",
    )
    max_iterations: int = Field(default=10, ge=1, le=50, description="Max tool execution loop iterations")


class AgentRunResponse(BaseModel):
    """Response payload returned by the agent harness."""
    status: str = "success"
    conversation_id: Optional[str] = None
    answer: str
    iterations: int = 1
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)


class ToolInfoResponse(BaseModel):
    """Metadata describing a registered tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    risk: str
    permission: str


class ToolListResponse(BaseModel):
    """List of all registered tools in the harness."""
    tools: List[ToolInfoResponse]


class ExecuteToolRequest(BaseModel):
    """Direct tool execution request payload."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ExecuteToolResponse(BaseModel):
    """Result of direct tool execution."""
    tool: str
    success: bool
    result: Any
