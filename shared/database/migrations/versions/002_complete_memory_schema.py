"""complete memory schema

Revision ID: 002_complete_memory_schema
Revises: 001_create_stm_tables
Create Date: 2026-08-13 10:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '002_complete_memory_schema'
down_revision: Union[str, None] = '001_create_stm_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update messages table
    op.add_column('messages', sa.Column('token_count', sa.Integer(), nullable=False, server_default='0'))
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'], unique=False)
    op.create_index('ix_messages_created_at', 'messages', ['created_at'], unique=False)

    # 2. Update context_summaries table
    op.add_column('context_summaries', sa.Column('token_count', sa.Integer(), nullable=False, server_default='0'))
    op.create_index('ix_context_summaries_conversation_id', 'context_summaries', ['conversation_id'], unique=False)
    op.create_index('ix_context_summaries_created_at', 'context_summaries', ['created_at'], unique=False)

    # 3. Create long_term_memories table
    op.create_table(
        'long_term_memories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.String(length=100), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('importance', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_long_term_memories_owner_id', 'long_term_memories', ['owner_id'], unique=False)
    op.create_index('ix_long_term_memories_key', 'long_term_memories', ['key'], unique=False)
    op.create_index('idx_ltm_owner_key', 'long_term_memories', ['owner_id', 'key'], unique=True)


def downgrade() -> None:
    # 1. Drop long_term_memories table
    op.drop_index('idx_ltm_owner_key', table_name='long_term_memories')
    op.drop_index('ix_long_term_memories_key', table_name='long_term_memories')
    op.drop_index('ix_long_term_memories_owner_id', table_name='long_term_memories')
    op.drop_table('long_term_memories')

    # 2. Revert context_summaries table
    op.drop_index('ix_context_summaries_created_at', table_name='context_summaries')
    op.drop_index('ix_context_summaries_conversation_id', table_name='context_summaries')
    op.drop_column('context_summaries', 'token_count')

    # 3. Revert messages table
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_column('messages', 'token_count')
