from app.pipeline.tools.meta.validation import ToolValidator, ArgumentValidator, ValidationError


_tool_validator = ToolValidator()
_arg_validator = ArgumentValidator()


class ToolExecutor:

    def __init__(self, registry):
        self.registry = registry

    async def execute(self, tool_name: str, arguments: dict):

        # 1. Resolve tool
        tool = self.registry.get(tool_name)
        if tool is None:
            raise ValueError(f"Tool '{tool_name}' is not registered")

        # 2. Phase 1 — schema validation (shape, types, unknown fields)
        _tool_validator.validate(tool_name, tool, arguments)

        # 3. Phase 2 — argument validation (values, coercion, cross-field)
        #    Note: validate_types() may mutate arguments in-place (safe coercion)
        _arg_validator.validate(tool, arguments)

        # 4. Execute
        result = tool.function(**arguments)
        if hasattr(result, "__await__"):
            result = await result

        return {
            "tool": tool_name,
            "success": True,
            "result": result,
        }