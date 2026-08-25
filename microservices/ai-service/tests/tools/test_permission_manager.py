"""Tests for PermissionManager — level-based access control with per-tool overrides."""

import pytest
from app.pipeline.tools.meta.policies.safety import Safety, Risk, PermissionLevel
from app.pipeline.tools.meta.policies.permission_manager import PermissionManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pm():
    return PermissionManager()


# Safety presets for testing
READ_SAFE = Safety(risk=Risk.LOW, permission=PermissionLevel.READ)
WRITE_SAFE = Safety(risk=Risk.MEDIUM, permission=PermissionLevel.WRITE)
DANGEROUS_SAFE = Safety(risk=Risk.HIGH, permission=PermissionLevel.DANGEROUS)
CRITICAL_SAFE = Safety(risk=Risk.CRITICAL, permission=PermissionLevel.DANGEROUS, requires_approval=True)


# ---------------------------------------------------------------------------
# Default permissions
# ---------------------------------------------------------------------------

class TestDefaults:

    def test_read_allowed_by_default(self, pm):
        assert pm.check("read_file", READ_SAFE) is True

    def test_write_allowed_by_default(self, pm):
        assert pm.check("write_file", WRITE_SAFE) is True

    def test_dangerous_denied_by_default(self, pm):
        assert pm.check("execute_command", DANGEROUS_SAFE) is False

    def test_critical_denied_by_default(self, pm):
        assert pm.check("docker", CRITICAL_SAFE) is False


# ---------------------------------------------------------------------------
# require() raises PermissionError
# ---------------------------------------------------------------------------

class TestRequire:

    def test_require_allowed_passes(self, pm):
        pm.require("read_file", READ_SAFE)  # should not raise

    def test_require_denied_raises(self, pm):
        with pytest.raises(PermissionError, match="Permission denied.*execute_command"):
            pm.require("execute_command", DANGEROUS_SAFE)

    def test_error_message_contains_permission_level(self, pm):
        with pytest.raises(PermissionError, match="dangerous"):
            pm.require("docker", CRITICAL_SAFE)


# ---------------------------------------------------------------------------
# Per-tool overrides
# ---------------------------------------------------------------------------

class TestOverrides:

    def test_allow_tool_overrides_denied_level(self, pm):
        assert pm.check("execute_command", DANGEROUS_SAFE) is False
        pm.allow_tool("execute_command")
        assert pm.check("execute_command", DANGEROUS_SAFE) is True

    def test_deny_tool_overrides_allowed_level(self, pm):
        assert pm.check("read_file", READ_SAFE) is True
        pm.deny_tool("read_file")
        assert pm.check("read_file", READ_SAFE) is False

    def test_clear_override_reverts_to_level(self, pm):
        pm.allow_tool("execute_command")
        assert pm.check("execute_command", DANGEROUS_SAFE) is True
        pm.clear_override("execute_command")
        assert pm.check("execute_command", DANGEROUS_SAFE) is False

    def test_clear_nonexistent_override_is_noop(self, pm):
        pm.clear_override("nonexistent")  # should not raise

    def test_require_with_override_passes(self, pm):
        pm.allow_tool("docker")
        pm.require("docker", CRITICAL_SAFE)  # should not raise

    def test_require_with_deny_override_raises(self, pm):
        pm.deny_tool("web_search")
        with pytest.raises(PermissionError):
            pm.require("web_search", READ_SAFE)


# ---------------------------------------------------------------------------
# Level toggles
# ---------------------------------------------------------------------------

class TestSetLevel:

    def test_enable_dangerous_level(self, pm):
        pm.set_level(PermissionLevel.DANGEROUS, True)
        assert pm.check("execute_command", DANGEROUS_SAFE) is True

    def test_disable_read_level(self, pm):
        pm.set_level(PermissionLevel.READ, False)
        assert pm.check("read_file", READ_SAFE) is False

    def test_disable_write_level(self, pm):
        pm.set_level(PermissionLevel.WRITE, False)
        assert pm.check("write_file", WRITE_SAFE) is False

    def test_override_takes_precedence_over_level(self, pm):
        """Per-tool override beats level toggle."""
        pm.set_level(PermissionLevel.DANGEROUS, True)
        pm.deny_tool("execute_command")
        assert pm.check("execute_command", DANGEROUS_SAFE) is False


# ---------------------------------------------------------------------------
# Introspection
# ---------------------------------------------------------------------------

class TestIntrospection:

    def test_get_level_status(self, pm):
        status = pm.get_level_status()
        assert status == {"read": True, "write": True, "dangerous": False}

    def test_get_level_status_after_change(self, pm):
        pm.set_level(PermissionLevel.DANGEROUS, True)
        status = pm.get_level_status()
        assert status["dangerous"] is True

    def test_get_overrides_empty(self, pm):
        assert pm.get_overrides() == {}

    def test_get_overrides_after_allow(self, pm):
        pm.allow_tool("docker")
        assert pm.get_overrides() == {"docker": True}

    def test_get_overrides_after_deny(self, pm):
        pm.deny_tool("read_file")
        assert pm.get_overrides() == {"read_file": False}

    def test_get_overrides_multiple(self, pm):
        pm.allow_tool("docker")
        pm.deny_tool("read_file")
        overrides = pm.get_overrides()
        assert overrides == {"docker": True, "read_file": False}
