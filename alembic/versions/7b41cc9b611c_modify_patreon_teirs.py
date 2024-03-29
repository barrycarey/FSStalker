"""modify patreon teirs

Revision ID: 7b41cc9b611c
Revises: 9de7dbaa4fa7
Create Date: 2022-09-30 19:26:16.584281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b41cc9b611c'
down_revision = '9de7dbaa4fa7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patreon_tiers', sa.Column('tier_id', sa.Integer(), nullable=True))
    op.add_column('patreon_tiers', sa.Column('tier_name', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('patreon_tiers', 'tier_name')
    op.drop_column('patreon_tiers', 'tier_id')
    # ### end Alembic commands ###
