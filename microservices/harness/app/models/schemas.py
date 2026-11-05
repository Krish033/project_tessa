import json
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field
from app.utils.clean_string import clean_string


class Fact(BaseModel):
    content: str
    key: Optional[str] = None
    importance: float = 0.5


class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: str
    content: str
    token_count: int = 0


class ToolCall(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    action: Literal["final", "tool"] = "final"
    answer: str = ""
    tool: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    ltm: List[str] = Field(default_factory=list)

    @property
    def is_final(self) -> bool:
        return self.action == "final"

    @property
    def is_tool(self) -> bool:
        return self.action == "tool"

    @property
    def tool_name(self) -> Optional[str]:
        return self.tool

    @property
    def ltm_facts(self) -> List[str]:
        return self.ltm

    def format_tool_call(self) -> str:
        return json.dumps({
            "action": "tool",
            "tool": self.tool,
            "arguments": self.arguments,
        })

    @classmethod
    def parse(cls, raw_response: str) -> "LLMResponse":
        """Parse cleaned JSON text into LLMResponse model; throws ValidationError on invalid schema."""
        cleaned = clean_string(raw_response)
        return cls.model_validate_json(cleaned)
