"""second migration

Revision ID: f01253cd5e35
Revises: 249cdc7930ed
Create Date: 2023-03-31 15:01:07.645623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f01253cd5e35'
down_revision = '249cdc7930ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('locked', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transactions', 'locked')
    # ### end Alembic commands ###