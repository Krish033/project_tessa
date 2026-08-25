"""
Permission Manager — controls which tools the agent is allowed to invoke.

Default policy:
    READ       → allowed
    WRITE      → allowed
    DANGEROUS  → denied

Per-tool overrides via allow_tool() / deny_tool().
Level-wide toggles via set_level().
"""

from __future__ import annotations

from app.pipeline.tools.meta.policies.safety import PermissionLevel, Safety


class PermissionManager:
    """
    Gate that answers: "Is the agent allowed to use this tool at all?"

    Resolution order:
      1. Per-tool override (allow_tool / deny_tool) — highest priority.
      2. Permission-level setting (set_level).
    """

    def __init__(self):
        self._level_allowed: dict[PermissionLevel, bool] = {
            PermissionLevel.READ: True,
            PermissionLevel.WRITE: True,
            PermissionLevel.DANGEROUS: False,
        }
        self._tool_overrides: dict[str, bool] = {}

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def check(self, tool_name: str, safety: Safety) -> bool:
        """Return True if the tool is allowed, False if denied."""
        # Per-tool override takes precedence
        if tool_name in self._tool_overrides:
            return self._tool_overrides[tool_name]

        # Fall back to permission-level setting
        return self._level_allowed.get(safety.permission, False)

    def require(self, tool_name: str, safety: Safety) -> None:
        """Raise PermissionError if the tool is denied."""
        if not self.check(tool_name, safety):
            raise PermissionError(
                f"Permission denied: '{tool_name}' requires "
                f"'{safety.permission.value}' permission (currently denied)"
            )

    # ------------------------------------------------------------------
    # Configuration API
    # ------------------------------------------------------------------

    def allow_tool(self, tool_name: str) -> None:
        """Explicitly allow a specific tool, overriding its level."""
        self._tool_overrides[tool_name] = True

    def deny_tool(self, tool_name: str) -> None:
        """Explicitly deny a specific tool, overriding its level."""
        self._tool_overrides[tool_name] = False

    def clear_override(self, tool_name: str) -> None:
        """Remove a per-tool override, reverting to level-based policy."""
        self._tool_overrides.pop(tool_name, None)

    def set_level(self, level: PermissionLevel, allowed: bool) -> None:
        """Enable or disable an entire permission level."""
        self._level_allowed[level] = allowed

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_level_status(self) -> dict[str, bool]:
        """Return current level permissions as a serializable dict."""
        return {level.value: allowed for level, allowed in self._level_allowed.items()}

    def get_overrides(self) -> dict[str, bool]:
        """Return current per-tool overrides."""
        return dict(self._tool_overrides)
