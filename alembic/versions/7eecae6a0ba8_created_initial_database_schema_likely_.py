"""Created initial database schema, likely will change

Revision ID: 7eecae6a0ba8
Revises: 
Create Date: 2025-02-01 16:37:52.745405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7eecae6a0ba8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('provider', sa.String(), nullable=True),
    sa.Column('magnetLink', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(), nullable=True),
    sa.Column('updatedAt', sa.DateTime(), nullable=True),
    sa.Column('functional', sa.Boolean(), nullable=True),
    sa.Column('tmdbId', sa.String(), nullable=True),
    sa.Column('season', sa.Integer(), nullable=True),
    sa.Column('episode', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_createdAt'), 'items', ['createdAt'], unique=False)
    op.create_index(op.f('ix_items_episode'), 'items', ['episode'], unique=False)
    op.create_index(op.f('ix_items_functional'), 'items', ['functional'], unique=False)
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_magnetLink'), 'items', ['magnetLink'], unique=False)
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)
    op.create_index(op.f('ix_items_provider'), 'items', ['provider'], unique=False)
    op.create_index(op.f('ix_items_season'), 'items', ['season'], unique=False)
    op.create_index(op.f('ix_items_tmdbId'), 'items', ['tmdbId'], unique=False)
    op.create_index(op.f('ix_items_updatedAt'), 'items', ['updatedAt'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_items_updatedAt'), table_name='items')
    op.drop_index(op.f('ix_items_tmdbId'), table_name='items')
    op.drop_index(op.f('ix_items_season'), table_name='items')
    op.drop_index(op.f('ix_items_provider'), table_name='items')
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_index(op.f('ix_items_magnetLink'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_index(op.f('ix_items_functional'), table_name='items')
    op.drop_index(op.f('ix_items_episode'), table_name='items')
    op.drop_index(op.f('ix_items_createdAt'), table_name='items')
    op.drop_table('items')
    # ### end Alembic commands ###
