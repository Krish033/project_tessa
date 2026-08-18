"""create tools table

Revision ID: 003_create_tools_table
Revises: 002_complete_memory_schema
Create Date: 2026-08-14 00:22:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = '003_create_tools_table'
down_revision: Union[str, None] = '002_complete_memory_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    use_pgvector = False

    if bind.dialect.name == 'postgresql':
        # Safely check if vector extension package is installed in PostgreSQL
        res = bind.execute(sa.text("SELECT name FROM pg_available_extensions WHERE name = 'vector'")).fetchone()
        if res is not None:
            op.execute('CREATE EXTENSION IF NOT EXISTS vector')
            use_pgvector = True
        else:
            use_pgvector = False
    else:
        # SQLite / in-memory unit tests
        use_pgvector = True

    embedding_type = Vector() if use_pgvector else sa.JSON()

    op.create_table(
        'tools',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('embedding', embedding_type, nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tool_name')
    )
    op.create_index('ix_tools_tool_name', 'tools', ['tool_name'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_tools_tool_name', table_name='tools')
    op.drop_table('tools')
