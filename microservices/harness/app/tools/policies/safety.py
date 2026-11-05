"""
Safety metadata types for the tool permission and policy system.

Every tool declares its own Safety metadata:

    class ReadFileTool:
        safety = Safety(risk=Risk.LOW, permission=PermissionLevel.READ)

    class ExecuteCommandTool:
        safety = Safety(
            risk=Risk.CRITICAL,
            permission=PermissionLevel.DANGEROUS,
            requires_approval=True,
        )

No giant if-else chains. 100 tools = 100 small declarations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Risk(Enum):
    """How dangerous a tool operation is."""
    LOW = "low"            # read_file, web_search, get_os_info
    MEDIUM = "medium"      # edit_file, write_file, create_pdf
    HIGH = "high"          # delete_file, send_email
    CRITICAL = "critical"  # execute_command, docker


class PermissionLevel(Enum):
    """Broad permission category a tool belongs to."""
    READ = "read"
    WRITE = "write"
    DANGEROUS = "dangerous"


@dataclass(frozen=True)
class Safety:
    """
    Immutable safety metadata declared by each tool.

    Attributes:
        risk:              Inherent risk level of the tool.
        permission:        Permission category (READ / WRITE / DANGEROUS).
        requires_approval: If True, CLI must prompt the user before execution.
        restricted_args:   Map of argument names to lists of forbidden
                           substrings. Example: {"path": [".env", "/etc"]}
    """
    risk: Risk = Risk.LOW
    permission: PermissionLevel = PermissionLevel.READ
    requires_approval: bool = False
    restricted_args: dict = field(default_factory=dict)


class SafetyError(Exception):
    """Raised when the safety policy denies an operation."""

    def __init__(self, reason: str, risk: Risk | None = None):
        self.reason = reason
        self.risk = risk
        super().__init__(reason)
