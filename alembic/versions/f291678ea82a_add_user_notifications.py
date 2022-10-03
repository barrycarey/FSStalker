"""Add user notifications

Revision ID: f291678ea82a
Revises: 7b41cc9b611c
Create Date: 2022-10-02 11:26:33.402336

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f291678ea82a'
down_revision = '7b41cc9b611c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('read', sa.Boolean(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(length=300), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('patreon_tiers', 'tier_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patreon_tiers', sa.Column('tier_name', mysql.VARCHAR(length=50), nullable=True))
    op.drop_table('user_notification')
    # ### end Alembic commands ###
