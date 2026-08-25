from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional

from app.pipeline.tools.meta.policies.safety import Safety


@dataclass
class Tool:
    name: str
    description: str
    function: Callable
    parameters: dict
    permissions: dict = field(default_factory=dict)   # legacy — kept for DB sync
    safety: Safety = field(default_factory=Safety)     # runtime permission + policy


# tool registry
class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    # Register tool
    def register(self, tool: Tool):
        if tool.name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool.name}"
            )
 
        self._tools[tool.name] = tool


    # gwt all the tools
    def get(self, name: str) -> Tool:
        tool = self._tools.get(name)

        if tool is None:
            raise KeyError(f"Tool not found: {name}")

        return tool


    # get all the tools
    def get_all(self) -> list[Tool]:
        return list(self._tools.values())


    # check if tool exists
    def exists(self, name: str) -> bool:
        return name in self._tools