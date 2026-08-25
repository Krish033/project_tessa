"""Tests for SafetyPolicy — operation-level safety evaluation."""

import pytest
from app.pipeline.tools.meta.policies.safety import Safety, Risk, PermissionLevel
from app.pipeline.tools.meta.policies.safety_policy import SafetyPolicy, PolicyDecision


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def policy():
    return SafetyPolicy()


# ---------------------------------------------------------------------------
# PolicyDecision basics
# ---------------------------------------------------------------------------

class TestPolicyDecision:

    def test_allowed_decision(self):
        d = PolicyDecision(allowed=True, denied=False, requires_approval=False, risk=Risk.LOW)
        assert d.allowed is True
        assert d.denied is False
        assert d.requires_approval is False
        assert d.risk is Risk.LOW

    def test_denied_decision(self):
        d = PolicyDecision(allowed=False, denied=True, requires_approval=False, risk=Risk.HIGH, reason="blocked")
        assert d.denied is True
        assert d.reason == "blocked"


# ---------------------------------------------------------------------------
# Basic evaluation — no restricted args
# ---------------------------------------------------------------------------

class TestEvaluateBasic:

    def test_low_risk_allowed(self, policy):
        safety = Safety(risk=Risk.LOW, permission=PermissionLevel.READ)
        decision = policy.evaluate("read_file", safety, {"path": "/tmp/test.txt"})
        assert decision.allowed is True
        assert decision.denied is False
        assert decision.risk is Risk.LOW

    def test_medium_risk_allowed(self, policy):
        safety = Safety(risk=Risk.MEDIUM, permission=PermissionLevel.WRITE)
        decision = policy.evaluate("edit_file", safety, {"path": "foo.py", "content": "x"})
        assert decision.allowed is True
        assert decision.denied is False

    def test_high_risk_allowed_with_approval(self, policy):
        safety = Safety(risk=Risk.HIGH, permission=PermissionLevel.DANGEROUS, requires_approval=True)
        decision = policy.evaluate("send_email", safety, {"to": "a@b.com"})
        assert decision.allowed is True
        assert decision.denied is False
        assert decision.requires_approval is True

    def test_critical_risk_allowed_with_approval(self, policy):
        safety = Safety(risk=Risk.CRITICAL, permission=PermissionLevel.DANGEROUS, requires_approval=True)
        decision = policy.evaluate("execute_command", safety, {"command": "ls"})
        assert decision.allowed is True
        assert decision.requires_approval is True
        assert decision.risk is Risk.CRITICAL

    def test_no_approval_by_default(self, policy):
        safety = Safety(risk=Risk.LOW)
        decision = policy.evaluate("web_search", safety, {"query": "python"})
        assert decision.requires_approval is False

    def test_empty_arguments(self, policy):
        safety = Safety(risk=Risk.LOW)
        decision = policy.evaluate("get_os_info", safety, {})
        assert decision.allowed is True


# ---------------------------------------------------------------------------
# Restricted argument patterns
# ---------------------------------------------------------------------------

class TestRestrictedArgs:

    def test_restricted_path_blocked(self, policy):
        safety = Safety(
            risk=Risk.HIGH,
            permission=PermissionLevel.DANGEROUS,
            restricted_args={"path": [".env", "/etc/shadow"]},
        )
        decision = policy.evaluate("delete_file", safety, {"path": "/project/.env"})
        assert decision.denied is True
        assert ".env" in decision.reason

    def test_restricted_path_etc_shadow(self, policy):
        safety = Safety(
            risk=Risk.HIGH,
            restricted_args={"path": ["/etc/shadow"]},
        )
        decision = policy.evaluate("read_file", safety, {"path": "/etc/shadow"})
        assert decision.denied is True

    def test_non_restricted_path_allowed(self, policy):
        safety = Safety(
            risk=Risk.HIGH,
            restricted_args={"path": [".env", "/etc"]},
        )
        decision = policy.evaluate("delete_file", safety, {"path": "/tmp/test.txt"})
        assert decision.allowed is True
        assert decision.denied is False

    def test_case_insensitive_match(self, policy):
        safety = Safety(
            risk=Risk.MEDIUM,
            restricted_args={"path": [".ENV"]},
        )
        decision = policy.evaluate("edit_file", safety, {"path": "/project/.env"})
        assert decision.denied is True

    def test_multiple_restricted_args(self, policy):
        safety = Safety(
            risk=Risk.CRITICAL,
            restricted_args={
                "command": ["rm -rf", "format"],
                "path": ["/sys"],
            },
        )
        decision = policy.evaluate("execute_command", safety, {"command": "rm -rf /", "path": "/tmp"})
        assert decision.denied is True
        assert "rm -rf" in decision.reason

    def test_restricted_arg_not_present_in_arguments(self, policy):
        """If the restricted arg isn't in the call, no violation."""
        safety = Safety(
            risk=Risk.HIGH,
            restricted_args={"path": [".env"]},
        )
        decision = policy.evaluate("some_tool", safety, {"query": "hello"})
        assert decision.allowed is True

    def test_restricted_arg_with_non_string_value(self, policy):
        """Non-string argument values are skipped (no crash)."""
        safety = Safety(
            risk=Risk.HIGH,
            restricted_args={"count": ["999"]},
        )
        decision = policy.evaluate("some_tool", safety, {"count": 42})
        assert decision.allowed is True

    def test_restricted_arg_with_none_value(self, policy):
        safety = Safety(
            risk=Risk.HIGH,
            restricted_args={"path": [".env"]},
        )
        decision = policy.evaluate("some_tool", safety, {"path": None})
        assert decision.allowed is True

    def test_multiple_violations_all_reported(self, policy):
        safety = Safety(
            risk=Risk.CRITICAL,
            restricted_args={"path": [".env", "/sys"]},
        )
        decision = policy.evaluate("delete_file", safety, {"path": "/sys/.env"})
        assert decision.denied is True
        # Both patterns should appear in the reason
        assert ".env" in decision.reason
        assert "/sys" in decision.reason

    def test_denied_decision_reason_contains_tool_name(self, policy):
        safety = Safety(
            risk=Risk.HIGH,
            restricted_args={"path": [".env"]},
        )
        decision = policy.evaluate("delete_file", safety, {"path": ".env"})
        assert "delete_file" in decision.reason
