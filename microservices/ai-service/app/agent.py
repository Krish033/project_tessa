import sys
import json
import asyncio
from typing import Any, List, Dict

# Ensure UTF-8 output encoding on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app.utils.json_response import JsonResponse
from app.utils.format_tool import format_tool_activity
from app.pipeline.tools.meta.policies.safety import SafetyError
from app.pipeline.memory.ltm import LongTermMemoryManager

_ltm_manager = LongTermMemoryManager()


class AgentLoop:
    """
    Executes the autonomous agent loop.

    Coordinates:
    - Building context (system prompt, retrieved tools, LTM, conversation history)
    - Querying the LLM
    - Parsing responses with JsonResponse
    - Executing tools via ToolExecutor
    - Storing extracted Long-Term Memory (LTM) facts
    """

    def __init__(self, ctx, llm, executor, max_iterations: int = 10, verbose: bool = True):
        self.ctx = ctx
        self.llm = llm
        self.executor = executor
        self.max_iterations = max_iterations
        self.verbose = verbose

    async def run(self, prompt: str) -> str:
        """Run the agent loop for a user prompt until final answer or max iterations."""
        self.ctx.add("user", prompt)

        for step in range(1, self.max_iterations + 1):
            messages = await self.ctx.build()
            _, raw_response = await self._call_llm(messages)

            # 1. Parse structured response
            response = JsonResponse.parse(raw_response)

            # 2. Persist LTM facts in background if present
            if response.ltm_facts:
                asyncio.create_task(self._store_ltm(response.ltm_facts))

            # 3. Handle Final Answer
            if response.is_final:
                self.ctx.add("assistant", response.answer)
                return response.answer

            # 4. Handle Tool Execution
            if response.is_tool and response.tool_name:
                if self.verbose:
                    print(format_tool_activity(response.tool_name, response.arguments))

                self.ctx.add("assistant", response.format_tool_call())
                tool_output = await self._execute_tool(response.tool_name, response.arguments)
                self.ctx.add("output", f"Tool '{response.tool_name}' execution result:\n{tool_output}")
                continue

            raise ValueError(f"Unknown LLM response action: {response.action} in response: {response.data}")

        return "Agent exceeded maximum iterations"

    async def _call_llm(self, messages: list) -> tuple[str, str]:
        """Execute LLM inference supporting both streaming and standard interfaces."""
        if hasattr(self.llm, "run_stream"):
            return await self.llm.run_stream(messages, on_reasoning=None, on_content=None)
        raw_response = self.llm.run(messages)
        return "", raw_response

    async def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool via executor and format results or errors safely."""
        try:
            execution = await self.executor.execute(tool_name, arguments)
            result = execution.get("result", str(execution))
        except PermissionError as e:
            result = f"⛔ Permission denied: {e}"
        except SafetyError as e:
            result = f"🛑 Safety policy blocked: {e}"
        except Exception as e:
            result = f"Error executing tool '{tool_name}': {str(e)}"

        if isinstance(result, (dict, list)):
            return json.dumps(result, indent=2, ensure_ascii=False)
        return str(result)

    async def _store_ltm(self, facts: list) -> None:
        """Persist LTM facts to DB with embeddings (fire-and-forget)."""
        owner_id = getattr(self.ctx, "conversation_id", "default_user")
        for fact in facts:
            if fact and isinstance(fact, str) and fact.strip():
                try:
                    await _ltm_manager.store_memory(
                        owner_id,
                        fact.strip(),
                    )
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ [Agent] LTM store failed: {e}")

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

            yield {"type": "raw_response", "step": step, "raw": raw_response}

            # Parse structured response
            response = JsonResponse.parse(raw_response)

            if response.ltm_facts:
                asyncio.create_task(self._store_ltm(response.ltm_facts))

            # 1. Handle Final Answer
            if response.is_final:
                self.ctx.add("assistant", response.answer)
                yield {"type": "content", "chunk": response.answer}
                yield {"type": "final", "answer": response.answer, "ltm": response.ltm_facts, "raw": raw_response}
                return

            # 2. Handle Tool Execution
            if response.is_tool and response.tool_name:
                self.ctx.add("assistant", response.format_tool_call())
                yield {"type": "tool_start", "tool": response.tool_name, "arguments": response.arguments}

                status = "success"
                try:
                    execution = await self.executor.execute(response.tool_name, response.arguments)
                    tool_output = execution.get("result", str(execution))
                except PermissionError as e:
                    tool_output = f"⛔ Permission denied: {e}"
                    status = "denied"
                except SafetyError as e:
                    tool_output = f"🛑 Safety policy blocked: {e}"
                    status = "denied"
                except Exception as e:
                    tool_output = f"Error executing tool '{response.tool_name}': {str(e)}"
                    status = "error"

                yield {"type": "tool_result", "tool": response.tool_name, "result": tool_output, "status": status}

                if isinstance(tool_output, (dict, list)):
                    formatted = json.dumps(tool_output, indent=2, ensure_ascii=False)
                else:
                    formatted = str(tool_output)

                self.ctx.add("output", f"Tool '{response.tool_name}' execution result:\n{formatted}")
                continue

            yield {"type": "error", "message": f"Unknown action: {response.action}"}
            return

        yield {"type": "error", "message": "Agent exceeded maximum iterations"}