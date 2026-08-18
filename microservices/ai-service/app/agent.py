import json
import re
import asyncio


def _extract_json_object(text: str):
    """Extract the first balanced JSON object from text using brace counting.
    Handles nested objects (e.g. tool arguments) correctly, unlike regex."""
    start = text.find('{')
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape_next = False
    for i in range(start, len(text)):
        c = text[i]
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
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None

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


class AgentLoop:
    """
    This class is for running the agent loop.
    It takes a context and an LLM and runs the agent loop.
    It supports tool calls, verbose logging, live reasoning & content streaming, and final responses.
    """

    def __init__(self, ctx, llm, executor, max_iterations=10, verbose=True):   
        self.ctx = ctx
        self.llm = llm
        self.executor = executor
        self.max_iterations = max_iterations
        self.verbose = verbose

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    async def run(self, prompt: str):
        self._log(f"\n🚀 [Agent] Starting execution for prompt: '{prompt}'")
        self.ctx.add("user", prompt)

        for step in range(1, self.max_iterations + 1):
            self._log(f"\n--- 🔄 Step {step}/{self.max_iterations} ---")
            
            # 1. Build messages context
            messages = await self.ctx.build()
            self._log(f"[Agent] Context built ({len(messages)} messages sent to LLM)")

            # 2. Run LLM with Streaming
            self._log("[Agent] Streaming LLM response...")

            reasoning_started = False
            content_started = False

            def handle_reasoning(chunk: str):
                nonlocal reasoning_started
                if not reasoning_started:
                    if self.verbose:
                        print_reasoning_start()
                    reasoning_started = True
                if self.verbose:
                    print_reasoning_chunk(chunk)

            def handle_content(chunk: str):
                nonlocal reasoning_started, content_started
                if reasoning_started and not content_started:
                    if self.verbose:
                        print_reasoning_end()
                if not content_started:
                    if self.verbose:
                        print_content_start()
                    content_started = True
                if self.verbose:
                    print_content_chunk(chunk)

            if hasattr(self.llm, "run_stream"):
                reasoning, raw_response = await self.llm.run_stream(
                    messages,
                    on_reasoning=handle_reasoning,
                    on_content=handle_content,
                )
            else:
                raw_response = self.llm.run(messages)
                reasoning = ""

            if self.verbose:
                if reasoning_started and not content_started:
                    print_reasoning_end()
                elif content_started:
                    print_content_end()

            # 3. Parse JSON response cleanly
            clean_str = raw_response.strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            elif clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]
            clean_str = clean_str.strip()

            try:
                response = json.loads(clean_str)
            except json.JSONDecodeError:
                # Balanced-brace extraction handles nested argument objects
                extracted = _extract_json_object(raw_response)
                if extracted and "action" in extracted:
                    response = extracted
                else:
                    self._log("[Agent] Warning: LLM output was not valid JSON. Wrapping as final response.")
                    response = {"action": "final", "answer": raw_response}

            action = response.get("action")

            # 4. Handle final response
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
                    self._log(f"📌 [Agent] LTM facts: {ltm}")
                    asyncio.create_task(self._store_ltm(ltm))
                self._log(f"✅ [Agent] Task Complete! Final Answer:\n{answer}\n")
                self.ctx.add("assistant", answer)
                return answer

            
            # 5. Handle tool execution (support "action": "tool" or "action": "<tool_name>")
            tool_name = None
            arguments = {}

            if action == "tool":
                tool_name = response.get("tool")
                arguments = response.get("arguments", {})
            elif action and hasattr(self.executor, "registry") and self.executor.registry.exists(action):
                tool_name = action
                arguments = response.get("arguments") or {k: v for k, v in response.items() if k != "action"}

            if tool_name:
                self._log(f"🛠️ [Agent] Executing tool: '{tool_name}' with arguments: {json.dumps(arguments)}")

                # Preserve assistant tool call in context history
                assistant_msg = json.dumps({"action": "tool", "tool": tool_name, "arguments": arguments})
                self.ctx.add("assistant", assistant_msg)

                try:
                    execution = await self.executor.execute(tool_name, arguments)
                    tool_output = execution.get("result", str(execution))
                    self._log(f"📥 [Agent] Tool Result:\n{tool_output}\n")
                except Exception as e:
                    tool_output = f"Error executing tool '{tool_name}': {str(e)}"
                    self._log(f"❌ [Agent] Tool Execution Error: {tool_output}\n")

                # Add clean tool output string into context history
                context_msg = f"Tool '{tool_name}' execution result:\n{tool_output}"
                self.ctx.add("output", context_msg)
                continue

            self._log(f"⚠️ [Agent] Unknown action: '{action}'")
            raise ValueError(f"Unknown LLM response action: {action} in response: {response}")

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
                    except asyncio.QueueEmpty:
                        await asyncio.sleep(0.005)

                while not queue.empty():
                    event = queue.get_nowait()
                    if event["type"] == "reasoning":
                        yield event

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
            clean_str = raw_response.strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            elif clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]
            clean_str = clean_str.strip()

            try:
                response = json.loads(clean_str)
            except json.JSONDecodeError:
                extracted = _extract_json_object(raw_response)
                if extracted and "action" in extracted:
                    response = extracted
                else:
                    response = {"action": "final", "answer": raw_response}

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
                except Exception as e:
                    tool_output = f"Error executing tool '{tool_name}': {str(e)}"
                    yield {"type": "tool_result", "tool": tool_name, "result": tool_output, "status": "error"}

                context_msg = f"Tool '{tool_name}' execution result:\n{tool_output}"
                self.ctx.add("output", context_msg)
                continue

            yield {"type": "error", "message": f"Unknown action: {action}"}
            return

        yield {"type": "error", "message": "Agent exceeded maximum iterations"}





    