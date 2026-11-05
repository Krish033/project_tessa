from app.pipeline.tools.meta.registry import Tool, ToolRegistry
from app.pipeline.tools.meta.policies.safety import Safety, Risk, PermissionLevel
from app.pipeline.context.memory.embedder import Embedder
from app.models.models import ToolModel
from app.core.database import db_session


def load_tools(registry: ToolRegistry, sync_db: bool = False):
    """
    Tool loader for registering tools into ToolRegistry.
    Tools have been cleared to build from scratch.
    """
    def reg(name: str, description: str, fn, schema: dict, safety: Safety = None):
        if safety is None:
            safety = Safety(risk=Risk.LOW, permission=PermissionLevel.READ)
        registry.register(
            Tool(
                name=name,
                description=description,
                function=fn,
                parameters=schema,
                safety=safety,
            )
        )

    # Empty tool set - ready to build from scratch

    if sync_db:
        try:
            sync_tools_to_db(registry)
        except Exception as e:
            print(f"Could not sync tools to DB: {e}")


def sync_tools_to_db(registry: ToolRegistry):
    embedder = Embedder()
    with db_session() as db:
        for tool in registry.get_all():
            existing = db.query(ToolModel).filter_by(name=tool.name).first()
            embedding = embedder.embed(f"{tool.name}: {tool.description}")

            if existing:
                existing.description = tool.description
                existing.parameters = tool.parameters
                existing.embedding = embedding
            else:
                db.add(
                    ToolModel(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.parameters,
                        embedding=embedding,
                    )
                )
