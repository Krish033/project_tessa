import sys
import json
import re
import asyncio

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _extract_json_object(text: str):
    """Extract the first balanced JSON object from text using brace counting.
    Handles nested objects (e.g. tool arguments) and unescaped newlines."""
    # Strip any think tags before scanning for JSON
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
                try:
                    return json.loads(cleaned[start:i + 1], strict=False)
                except json.JSONDecodeError:
                    return None
    return None

from app.pipeline.tools.meta.policies.safety import SafetyError

from app.ui.cli import (
    print_reasoning_start,
    print_reasoning_chunk,
    print_reasoning_end,
    print_content_start,
    print_content_chunk,
    print_content_end,
)
from app.pipeline.memory.ltm import LongTermMemoryManager

_ltm_manager = LongTermMemoryManager()


def _format_tool_activity(tool_name: str, arguments: dict) -> str:
    """Format tool call into a concise, human-readable activity status line."""
    if tool_name in ("web_search", "search_web", "google_search"):
        query = arguments.get("query") or arguments.get("q") or ""
        return f"🔍 Searching the web for '{query}'..." if query else "🔍 Searching the web..."
    elif tool_name in ("news_search", "search_news"):
        query = arguments.get("query") or arguments.get("q") or ""
        return f"📰 Searching news for '{query}'..." if query else "📰 Searching news..."
    elif tool_name in ("get_os_info", "system_info", "get_system_info"):
        return "💻 Checking system information..."
    elif tool_name in ("fetch_url", "read_url", "get_url"):
        url = arguments.get("url") or ""
        return f"🌐 Fetching webpage '{url}'..." if url else "🌐 Fetching webpage..."
    elif tool_name in ("execute_command", "run_command", "bash", "cmd"):
        cmd = arguments.get("command") or arguments.get("cmd") or ""
        return f"⚡ Running command: '{cmd}'..." if cmd else "⚡ Executing command..."
    elif tool_name in ("task_list", "list_tasks"):
        return "📋 Checking task list..."
    elif tool_name in ("maps_search", "nearby_places"):
        query = arguments.get("query") or arguments.get("location") or ""
        return f"📍 Looking up location '{query}'..." if query else "📍 Looking up locations..."
    else:
        return f"⚙️ Running {tool_name}..."


class AgentLoop:
    """
    This class is for running the agent loop.
    It takes a context and an LLM and runs the agent loop with clean, minimal status logging.
    """

    def __init__(self, ctx, llm, executor, max_iterations=10, verbose=True):   
        self.ctx = ctx
        self.llm = llm
        self.executor = executor
        self.max_iterations = max_iterations
        self.verbose = verbose

    async def run(self, prompt: str) -> str:
        self.ctx.add("user", prompt)

        for step in range(1, self.max_iterations + 1):
            messages = await self.ctx.build()

            if hasattr(self.llm, "run_stream"):
                reasoning, raw_response = await self.llm.run_stream(
                    messages,
                    on_reasoning=None,
                    on_content=None,
                )
            else:
                raw_response = self.llm.run(messages)

            # Parse JSON response cleanly
            clean_str = re.sub(r'<think>[\s\S]*?</think>', '', raw_response, flags=re.IGNORECASE).strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            elif clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]
            clean_str = clean_str.strip()

            try:
                response = json.loads(clean_str, strict=False)
            except json.JSONDecodeError:
                extracted = _extract_json_object(clean_str)
                if extracted and "action" in extracted:
                    response = extracted
                else:
                    ans_match = re.search(r'"answer"\s*:\s*"([\s\S]*?)"\s*(?:,\s*"ltm"|\}\s*$)', clean_str)
                    if ans_match:
                        response = {"action": "final", "answer": ans_match.group(1)}
                    else:
                        response = {"action": "final", "answer": clean_str}

            action = response.get("action")

            # Handle final response
            if action == "final":
                answer = response.get("answer", "")
                if isinstance(answer, (dict, list)):
                    answer = json.dumps(answer, indent=2)
                elif isinstance(answer, str):
                    if "\\n" in answer:
                        answer = answer.replace("\\n", "\n")
                    if "\\t" in answer:
                        answer = answer.replace("\\t", "\t")
                    if '\\"' in answer:
                        answer = answer.replace('\\"', '"')
                    answer = answer.strip()
                    if answer.startswith('"') and answer.endswith('"') and len(answer) > 1:
                        answer = answer[1:-1]

                ltm = response.get("ltm", [])
                if isinstance(ltm, list) and ltm:
                    asyncio.create_task(self._store_ltm(ltm))

                self.ctx.add("assistant", answer)
                return answer

            # Handle tool execution
            tool_name = None
            arguments = {}

            if action == "tool":
                tool_name = response.get("tool")
                arguments = response.get("arguments", {})
            elif action and hasattr(self.executor, "registry") and self.executor.registry.exists(action):
                tool_name = action
                arguments = response.get("arguments") or {k: v for k, v in response.items() if k != "action"}

            if tool_name:
                if self.verbose:
                    print(_format_tool_activity(tool_name, arguments))

                assistant_msg = json.dumps({"action": "tool", "tool": tool_name, "arguments": arguments})
                self.ctx.add("assistant", assistant_msg)

                try:
                    execution = await self.executor.execute(tool_name, arguments)
                    tool_output = execution.get("result", str(execution))
                except PermissionError as e:
                    tool_output = f"⛔ Permission denied: {e}"
                except SafetyError as e:
                    tool_output = f"🛑 Safety policy blocked: {e}"
                except Exception as e:
                    tool_output = f"Error executing tool '{tool_name}': {str(e)}"

                context_msg = f"Tool '{tool_name}' execution result:\n{tool_output}"
                self.ctx.add("output", context_msg)
                continue

            raise ValueError(f"Unknown LLM response action: {action} in response: {response}")

        return "Agent exceeded maximum iterations"

    async def _store_ltm(self, facts: list) -> None:
        """Persist LTM facts to DB with embeddings (fire-and-forget)."""
        owner_id = getattr(self.ctx, "conversation_id", "default_user")
        for fact in facts:
            if fact and isinstance(fact, str) and fact.strip():
                try:
                    await asyncio.to_thread(
                        _ltm_manager.store_memory,
                        owner_id,
                        fact.strip(),
                    )
                except Exception as e:
                    self._log(f"⚠️ [Agent] LTM store failed: {e}")

    async def run_event_stream(self, prompt: str):
        """
        Async generator yielding real-time execution events for SSE streaming.
        Events: start, step, reasoning, content, tool_start, tool_result, final, error
        """
        yield {"type": "start", "prompt": prompt}
        self.ctx.add("user", prompt)

        for step in range(1, self.max_iterations + 1):
            yield {"type": "step", "step": step, "max_iterations": self.max_iterations}

            messages = await self.ctx.build()
            queue = asyncio.Queue()

            def handle_reasoning(chunk: str):
                queue.put_nowait({"type": "reasoning", "chunk": chunk})

            def handle_content(chunk: str):
                # Queue content chunks internally per step
                queue.put_nowait({"type": "content_chunk", "chunk": chunk})

            if hasattr(self.llm, "run_stream"):
                llm_task = asyncio.create_task(
                    self.llm.run_stream(
                        messages,
                        on_reasoning=handle_reasoning,
                        on_content=handle_content,
                    )
                )

                while not llm_task.done():
                    try:
                        event = queue.get_nowait()
                        if event["type"] == "reasoning":
                            yield event
                        elif event["type"] == "content_chunk":
                            yield {"type": "content", "chunk": event["chunk"]}
                    except asyncio.QueueEmpty:
                        await asyncio.sleep(0.005)

                while not queue.empty():
                    event = queue.get_nowait()
                    if event["type"] == "reasoning":
                        yield event
                    elif event["type"] == "content_chunk":
                        yield {"type": "content", "chunk": event["chunk"]}

                try:
                    reasoning, raw_response = await llm_task
                except Exception as e:
                    yield {"type": "error", "message": f"LLM error: {str(e)}"}
                    return
            else:
                raw_response = self.llm.run(messages)
                reasoning = ""

            # Emit raw response event
            yield {"type": "raw_response", "step": step, "raw": raw_response}

            # Parse JSON response
            clean_str = re.sub(r'<think>[\s\S]*?</think>', '', raw_response, flags=re.IGNORECASE).strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            elif clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]
            clean_str = clean_str.strip()

            try:
                response = json.loads(clean_str, strict=False)
            except json.JSONDecodeError:
                extracted = _extract_json_object(clean_str)
                if extracted and "action" in extracted:
                    response = extracted
                else:
                    # Regex fallback if answer string has unescaped quotes/syntax issues
                    ans_match = re.search(r'"answer"\s*:\s*"([\s\S]*?)"\s*(?:,\s*"ltm"|\}\s*$)', clean_str)
                    if ans_match:
                        response = {"action": "final", "answer": ans_match.group(1)}
                    else:
                        response = {"action": "final", "answer": clean_str}

            action = response.get("action")

            if action == "final":
                answer = response.get("answer", "")
                if isinstance(answer, (dict, list)):
                    answer = json.dumps(answer, indent=2)
                elif isinstance(answer, str):
                    if "\\n" in answer:
                        answer = answer.replace("\\n", "\n")
                    if "\\t" in answer:
                        answer = answer.replace("\\t", "\t")
                    if '\\"' in answer:
                        answer = answer.replace('\\"', '"')
                    answer = answer.strip()
                    if answer.startswith('"') and answer.endswith('"') and len(answer) > 1:
                        answer = answer[1:-1]

                self.ctx.add("assistant", answer)
                ltm = response.get("ltm", [])
                if not isinstance(ltm, list):
                    ltm = []
                if ltm:
                    asyncio.create_task(self._store_ltm(ltm))

                # Yield clean final answer stream to the UI
                yield {"type": "content", "chunk": answer}
                yield {"type": "final", "answer": answer, "ltm": ltm, "raw": raw_response}
                return

            tool_name = None
            arguments = {}

            if action == "tool":
                tool_name = response.get("tool")
                arguments = response.get("arguments", {})
            elif action and hasattr(self.executor, "registry") and self.executor.registry.exists(action):
                tool_name = action
                arguments = response.get("arguments") or {k: v for k, v in response.items() if k != "action"}

            if tool_name:
                # Record assistant tool call in context history
                assistant_msg = json.dumps({"action": "tool", "tool": tool_name, "arguments": arguments})
                self.ctx.add("assistant", assistant_msg)

                yield {"type": "tool_start", "tool": tool_name, "arguments": arguments}

                try:
                    execution = await self.executor.execute(tool_name, arguments)
                    tool_output = execution.get("result", str(execution))
                    yield {"type": "tool_result", "tool": tool_name, "result": tool_output, "status": "success"}
                except PermissionError as e:
                    tool_output = f"⛔ Permission denied: {e}"
                    yield {"type": "tool_result", "tool": tool_name, "result": tool_output, "status": "denied"}
                except SafetyError as e:
                    tool_output = f"🛑 Safety policy blocked: {e}"
                    yield {"type": "tool_result", "tool": tool_name, "result": tool_output, "status": "denied"}
                except Exception as e:
                    tool_output = f"Error executing tool '{tool_name}': {str(e)}"
                    yield {"type": "tool_result", "tool": tool_name, "result": tool_output, "status": "error"}

                context_msg = f"Tool '{tool_name}' execution result:\n{tool_output}"
                self.ctx.add("output", context_msg)
                continue

            yield {"type": "error", "message": f"Unknown action: {action}"}
            return

        yield {"type": "error", "message": "Agent exceeded maximum iterations"}





    