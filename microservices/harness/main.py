import sys
from pathlib import Path

# Add project root to sys.path so microservices and shared can be imported directly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio

# Ensure UTF-8 output encoding on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from microservices.harness.app.tools.registry import ToolRegistry
from microservices.harness.app.tools.loader import load_tools
from microservices.harness.app.tools.executor import ToolExecutor
from microservices.harness.app.context.manager import ContextManager
from microservices.harness.app.loop import AgentLoop

async def main():
    # 1. Initialize tool registry & executor
    registry = ToolRegistry()
    load_tools(registry)
    executor = ToolExecutor(registry=registry)

    # 2. Initialize Context Manager (LLM moved to intelligence service)
    context_manager = ContextManager()

    agent = AgentLoop(
            ctx=context_manager,
            llm=None,
            executor=executor,
            max_iterations=20,
            verbose=True,
        )

    prompt = "Hii there! Can you tell me a joke?"

    response = await agent.run(prompt)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
