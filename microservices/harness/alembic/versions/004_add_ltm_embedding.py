"""add embedding column to long_term_memories

Revision ID: 004_add_ltm_embedding
Revises: 003_create_tools_table
Create Date: 2026-08-14 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = '004_add_ltm_embedding'
down_revision: Union[str, None] = '003_create_tools_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    use_pgvector = False

    if bind.dialect.name == 'postgresql':
        # Check if pgvector extension is already installed
        res = bind.execute(sa.text("SELECT extname FROM pg_extension WHERE extname = 'vector'")).fetchone()
        use_pgvector = res is not None
    else:
        # SQLite / in-memory unit tests
        use_pgvector = True

    embedding_type = Vector(768) if use_pgvector else sa.JSON()

    op.add_column('long_term_memories', sa.Column('embedding', embedding_type, nullable=True))


def downgrade() -> None:
    op.drop_column('long_term_memories', 'embedding')
