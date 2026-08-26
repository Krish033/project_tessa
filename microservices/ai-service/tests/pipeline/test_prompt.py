from app.core.prompt import SYSTEM_PROMPT


def test_system_prompt_structure():
    assert "RESPONSE FORMAT:" in SYSTEM_PROMPT
    assert '"action": "tool"' in SYSTEM_PROMPT
    assert '"action": "final"' in SYSTEM_PROMPT
    assert "LTM INSTRUCTIONS:" in SYSTEM_PROMPT
    assert "RULES:" in SYSTEM_PROMPT
