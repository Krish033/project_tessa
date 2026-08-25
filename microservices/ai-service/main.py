import sys
import asyncio

# Ensure UTF-8 output encoding on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app.pipeline.tools.meta.registry import ToolRegistry
from app.pipeline.tools.loader import load_tools
from app.pipeline.tools.meta.executor import ToolExecutor
from app.pipeline.llm import QwenLLM
from app.pipeline.context.manager import ContextManager
from app.agent import AgentLoop


async def main():
    # 1. Initialize tool registry & executor
    registry = ToolRegistry()
    load_tools(registry)
    executor = ToolExecutor(registry=registry)

    # 2. Initialize LLM & Context Manager
    llm = QwenLLM()
    context_manager = ContextManager(llm=llm)

    # 3. Initialize Agent Loop
    agent = AgentLoop(
        ctx=context_manager,
        llm=llm,
        executor=executor,
        max_iterations=10,
        verbose=True,
    )

    # 4. Static prompt for execution
    prompt = "Give me a brief summary of the available tools and verify system info."

    response = await agent.run(prompt)

    print(response)

if __name__ == "__main__":
    asyncio.run(main())