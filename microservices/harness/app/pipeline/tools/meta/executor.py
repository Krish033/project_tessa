"""
Tool Executor — the final pipeline stage.

Execution order:
  1. Resolve tool from registry
  2. Phase 1 — Schema validation (shape, types, unknown fields)
  3. Phase 2 — Argument validation (values, coercion, cross-field)
  4. Phase 3 — Permission check (is the agent allowed to use this tool?)
  5. Phase 4 — Safety policy (is this specific operation safe?)
  6. Phase 5 — Approval gate (CLI prompt for requires_approval tools)
  7. Execute the tool function
"""

from __future__ import annotations

import sys

from app.pipeline.tools.meta.validation import ToolValidator, ArgumentValidator, ValidationError
from app.pipeline.tools.meta.policies.safety import SafetyError
from app.pipeline.tools.meta.policies.permission_manager import PermissionManager
from app.pipeline.tools.meta.policies.safety_policy import SafetyPolicy


_tool_validator = ToolValidator()
_arg_validator = ArgumentValidator()


class ToolExecutor:

    def __init__(self, registry, permission_manager=None, safety_policy=None):
        self.registry = registry
        self.permission = permission_manager or PermissionManager()
        self.policy = safety_policy or SafetyPolicy()

    async def execute(self, tool_name: str, arguments: dict):

        # 1. Resolve tool
        tool = self.registry.get(tool_name)
        if tool is None:
            raise ValueError(f"Tool '{tool_name}' is not registered")

        # 2. Phase 1 — schema validation (shape, types, unknown fields)
        _tool_validator.validate(tool_name, tool, arguments)

        # 3. Phase 2 — argument validation (values, coercion, cross-field)
        #    Note: validate_types() may mutate arguments in-place (safe coercion)
        _arg_validator.validate(tool, arguments)

        # 4. Phase 3 — permission check
        self.permission.require(tool_name, tool.safety)

        # 5. Phase 4 — safety policy evaluation
        decision = self.policy.evaluate(tool_name, tool.safety, arguments)

        if decision.denied:
            raise SafetyError(decision.reason, decision.risk)

        # 6. Phase 5 — approval gate (CLI interactive prompt)
        if decision.requires_approval:
            approved = self._prompt_approval(tool_name, arguments)
            if not approved:
                raise SafetyError(
                    f"User denied approval for '{tool_name}'",
                    decision.risk,
                )

        # 7. Execute
        result = tool.function(**arguments)
        if hasattr(result, "__await__"):
            result = await result

        return {
            "tool": tool_name,
            "success": True,
            "result": result,
        }

    # ------------------------------------------------------------------
    # Approval gate
    # ------------------------------------------------------------------

    def _prompt_approval(self, tool_name: str, arguments: dict) -> bool:
        """
        Interactive CLI prompt for tools that require human approval.
        Returns True if the user approves, False if denied.
        """
        print(f"\n⚠️  Tool '{tool_name}' requires approval.")
        print(f"   Arguments: {arguments}")

        try:
            answer = input("   Approve execution? [y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return False

        return answer in ("y", "yes")