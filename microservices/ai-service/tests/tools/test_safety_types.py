"""Tests for Safety metadata types — Risk, PermissionLevel, Safety dataclass."""

import pytest
from app.pipeline.tools.meta.policies.safety import (
    Risk,
    PermissionLevel,
    Safety,
    SafetyError,
)


# ---------------------------------------------------------------------------
# Risk enum
# ---------------------------------------------------------------------------

class TestRisk:

    def test_values(self):
        assert Risk.LOW.value == "low"
        assert Risk.MEDIUM.value == "medium"
        assert Risk.HIGH.value == "high"
        assert Risk.CRITICAL.value == "critical"

    def test_all_members(self):
        assert set(Risk) == {Risk.LOW, Risk.MEDIUM, Risk.HIGH, Risk.CRITICAL}

    def test_from_value(self):
        assert Risk("low") is Risk.LOW
        assert Risk("critical") is Risk.CRITICAL


# ---------------------------------------------------------------------------
# PermissionLevel enum
# ---------------------------------------------------------------------------

class TestPermissionLevel:

    def test_values(self):
        assert PermissionLevel.READ.value == "read"
        assert PermissionLevel.WRITE.value == "write"
        assert PermissionLevel.DANGEROUS.value == "dangerous"

    def test_all_members(self):
        assert set(PermissionLevel) == {
            PermissionLevel.READ,
            PermissionLevel.WRITE,
            PermissionLevel.DANGEROUS,
        }


# ---------------------------------------------------------------------------
# Safety dataclass
# ---------------------------------------------------------------------------

class TestSafety:

    def test_defaults(self):
        s = Safety()
        assert s.risk is Risk.LOW
        assert s.permission is PermissionLevel.READ
        assert s.requires_approval is False
        assert s.restricted_args == {}

    def test_custom_values(self):
        s = Safety(
            risk=Risk.CRITICAL,
            permission=PermissionLevel.DANGEROUS,
            requires_approval=True,
            restricted_args={"path": [".env"]},
        )
        assert s.risk is Risk.CRITICAL
        assert s.permission is PermissionLevel.DANGEROUS
        assert s.requires_approval is True
        assert s.restricted_args == {"path": [".env"]}

    def test_frozen_immutability(self):
        s = Safety()
        with pytest.raises(AttributeError):
            s.risk = Risk.HIGH

    def test_frozen_immutability_permission(self):
        s = Safety()
        with pytest.raises(AttributeError):
            s.permission = PermissionLevel.DANGEROUS

    def test_frozen_immutability_approval(self):
        s = Safety()
        with pytest.raises(AttributeError):
            s.requires_approval = True

    def test_equality(self):
        a = Safety(risk=Risk.LOW, permission=PermissionLevel.READ)
        b = Safety(risk=Risk.LOW, permission=PermissionLevel.READ)
        assert a == b

    def test_inequality(self):
        a = Safety(risk=Risk.LOW)
        b = Safety(risk=Risk.HIGH)
        assert a != b

    def test_not_hashable_with_dict_field(self):
        """Safety with restricted_args (dict) is not hashable — expected."""
        s = Safety(risk=Risk.MEDIUM)
        with pytest.raises(TypeError):
            hash(s)


# ---------------------------------------------------------------------------
# SafetyError exception
# ---------------------------------------------------------------------------

class TestSafetyError:

    def test_basic(self):
        err = SafetyError("blocked")
        assert str(err) == "blocked"
        assert err.reason == "blocked"
        assert err.risk is None

    def test_with_risk(self):
        err = SafetyError("denied", Risk.CRITICAL)
        assert err.reason == "denied"
        assert err.risk is Risk.CRITICAL

    def test_is_exception(self):
        with pytest.raises(SafetyError):
            raise SafetyError("test")
