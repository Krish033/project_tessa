import json
import re
from typing import Any, Optional, List
from app.utils.clean_string import clean_string


def sanitize_json_escapes(json_str: str) -> str:
    """Fix invalid backslash escapes in JSON strings produced by LLMs (e.g. \\. -> \\\\.)."""
    pattern = r'\\(?![/\\bfnrt"]|u[0-9a-fA-F]{4})'
    return re.sub(pattern, r'\\\\', json_str)


# Alias for backward compatibility
_sanitize_json_escapes = sanitize_json_escapes


def extract_json_object(text: str) -> Optional[dict]:
    """
    Extract the first balanced JSON object from text using brace counting.
    Handles nested objects (e.g. tool arguments) and unescaped newlines.
    """
    cleaned = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE).strip()
    start = cleaned.find('{')
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i in range(start, len(cleaned)):
        c = cleaned[i]
        if escape_next:
            escape_next = False
            continue
        if c == '\\' and in_string:
            escape_next = True
            continue
        if c == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                substr = cleaned[start:i + 1]
                try:
                    res = json.loads(substr, strict=False)
                    return res if isinstance(res, dict) else None
                except json.JSONDecodeError:
                    try:
                        res = json.loads(sanitize_json_escapes(substr), strict=False)
                        return res if isinstance(res, dict) else None
                    except json.JSONDecodeError:
                        return None
    return None


# Alias for backward compatibility
_extract_json_object = extract_json_object


class JsonResponse:
    """
    Parses and standardizes raw LLM responses into structured agent actions.

    Handles:
    - Stripping <think>...</think> reasoning tags
    - Stripping markdown code blocks (```json ... ```)
    - Repairing malformed JSON backslashes
    - Extracting balanced JSON objects
    - Normalizing final answers and tool arguments
    """

    def __init__(
        self,
        raw: str,
        data: dict,
        action: str,
        answer: str = "",
        tool_name: Optional[str] = None,
        arguments: Optional[dict] = None,
        ltm_facts: Optional[List[str]] = None,
    ):
        self.raw = raw
        self.data = data
        self.action = action
        self.answer = answer
        self.tool_name = tool_name
        self.arguments = arguments or {}
        self.ltm_facts = ltm_facts or []

    @property
    def is_final(self) -> bool:
        """True if the agent has reached a final answer."""
        return self.action == "final"

    @property
    def is_tool(self) -> bool:
        """True if the agent requested a tool execution."""
        return self.action == "tool" or bool(self.tool_name)

    def format_tool_call(self) -> str:
        """Format as a JSON string to record the assistant tool call in context history."""
        return json.dumps({
            "action": "tool",
            "tool": self.tool_name,
            "arguments": self.arguments,
        })

    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-like access for backward compatibility."""
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like indexing for backward compatibility."""
        return self.data[key]

    @classmethod
    def parse(cls, raw_response: str) -> "JsonResponse":
        """Factory method: Parse raw LLM output into a clean JsonResponse instance."""
        if not raw_response:
            return cls(raw="", data={"action": "final", "answer": ""}, action="final", answer="")

        clean_text = clean_string(raw_response)
        parsed_dict = cls._decode_json(clean_text)

        action = parsed_dict.get("action", "final")
        ltm_facts = cls._extract_ltm(parsed_dict)

        # 1. Final Answer Action
        if action == "final":
            raw_answer = parsed_dict.get("answer", "")
            answer = cls._clean_answer(raw_answer)
            return cls(
                raw=raw_response,
                data=parsed_dict,
                action="final",
                answer=answer,
                ltm_facts=ltm_facts,
            )

        # 2. Tool Execution Action
        tool_name = parsed_dict.get("tool")
        arguments = parsed_dict.get("arguments", {})

        # Handle models returning tool name directly in action (e.g. {"action": "web_search", "query": "..."})
        if not tool_name and action not in ("final", "tool"):
            tool_name = action
            arguments = parsed_dict.get("arguments") or {
                k: v for k, v in parsed_dict.items() if k not in ("action", "ltm")
            }

        return cls(
            raw=raw_response,
            data=parsed_dict,
            action=action,
            tool_name=tool_name,
            arguments=arguments,
            ltm_facts=ltm_facts,
        )

    @classmethod
    def _decode_json(cls, clean_text: str) -> dict:
        """Multi-pass JSON decoder with escape sanitation and fallback extractors."""
        # Pass 1: Direct JSON parse
        try:
            res = json.loads(clean_text, strict=False)
            if isinstance(res, dict):
                return res
            # Primitive value like "1200" or 1200
            return {"action": "final", "answer": str(res)}
        except json.JSONDecodeError:
            pass

        # Pass 2: Repair broken backslash escapes
        try:
            sanitized = sanitize_json_escapes(clean_text)
            res = json.loads(sanitized, strict=False)
            if isinstance(res, dict):
                return res
            return {"action": "final", "answer": str(res)}
        except json.JSONDecodeError:
            pass

        # Pass 3: Balanced brace extraction
        extracted = extract_json_object(clean_text)
        if extracted and isinstance(extracted, dict) and "action" in extracted:
            return extracted

        # Pass 4: Regex search for "answer" field
        ans_match = re.search(r'"answer"\s*:\s*"([\s\S]*?)"\s*(?:,\s*"ltm"|\}\s*$)', clean_text)
        if ans_match:
            return {"action": "final", "answer": ans_match.group(1)}

        # Pass 5: Fallback text
        return {"action": "final", "answer": clean_text}

    @staticmethod
    def _clean_answer(answer: Any) -> str:
        """Format and clean final answer string."""
        if isinstance(answer, (dict, list)):
            return json.dumps(answer, indent=2)
        if not isinstance(answer, str):
            return str(answer)

        # Unescape literal escape characters if present
        if "\\n" in answer:
            answer = answer.replace("\\n", "\n")
        if "\\t" in answer:
            answer = answer.replace("\\t", "\t")
        if '\\"' in answer:
            answer = answer.replace('\\"', '"')

        answer = answer.strip()
        # Remove accidental surrounding quotes
        if answer.startswith('"') and answer.endswith('"') and len(answer) > 1:
            answer = answer[1:-1]

        return answer

    @staticmethod
    def _extract_ltm(data: dict) -> List[str]:
        """Extract and sanitize durable long-term memory facts."""
        ltm = data.get("ltm", [])
        if isinstance(ltm, list):
            return [str(f).strip() for f in ltm if f and str(f).strip()]
        return []
