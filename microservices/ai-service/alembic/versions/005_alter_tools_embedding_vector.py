"""alter tools embedding column to vector(768)

Revision ID: 005_alter_tools_embedding_vector
Revises: 004_add_ltm_embedding
Create Date: 2026-08-15 01:38:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = '005_alter_tools_embedding_vector'
down_revision: Union[str, None] = '004_add_ltm_embedding'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('ALTER TABLE tools ALTER COLUMN embedding TYPE vector(768) USING NULL;')


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('ALTER TABLE tools ALTER COLUMN embedding TYPE json USING NULL;')
