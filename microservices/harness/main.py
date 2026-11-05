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
from app.pipeline.context.manager import ContextManager


async def main():
    # 1. Initialize tool registry & executor
    registry = ToolRegistry()
    load_tools(registry)
    executor = ToolExecutor(registry=registry)

    # 2. Initialize Context Manager (LLM moved to intelligence service)
    context_manager = ContextManager()

    print("Harness initialized successfully.")
    print(f"Registered tools count: {len(registry.get_all())}")


if __name__ == "__main__":
    asyncio.run(main())
