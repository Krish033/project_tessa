from app.models.schemas import LLMResponse
from app.pipeline.context.memory.ltm import LongTermMemoryManager
from app.utils.format_tool import format_tool_activity

_ltm_manager = LongTermMemoryManager()


class AgentLoop:
    """Executes the autonomous agent loop."""

    def __init__(self, ctx, llm, executor, max_iterations: int = 10, verbose: bool = True):
        self.ctx = ctx
        self.llm = llm
        self.executor = executor
        self.max_iterations = max_iterations
        self.verbose = verbose

    async def run(self, prompt: str) -> str:
        self.ctx.add("user", prompt)

        for _ in range(self.max_iterations):
            messages = await self.ctx.build()
            response = LLMResponse.parse(self.llm.run(messages))

            # Store any long-term memories extracted by the model
            for fact in response.ltm:
                await _ltm_manager.store_memory(getattr(self.ctx, "conversation_id", "default_user"), fact)

            # Final answer
            if response.is_final:
                self.ctx.add("assistant", response.answer)
                return response.answer

            # Tool execution
            if response.is_tool:
                if self.verbose:
                    print(format_tool_activity(response.tool_name, response.arguments))

                self.ctx.add("assistant", response.format_tool_call())
                try:
                    execution = await self.executor.execute(response.tool_name, response.arguments)
                    result = execution.get("result", execution)
                except Exception as e:
                    result = f"Error: {e}"

                self.ctx.add("output", f"Tool '{response.tool_name}' execution result:\n{result}")

        return "Agent exceeded maximum iterations"