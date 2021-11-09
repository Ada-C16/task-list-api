"""empty message

Revision ID: 84cdfb8bbe01
Revises: 400a906a3aa5
Create Date: 2021-10-30 10:13:09.703720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84cdfb8bbe01'
down_revision = '400a906a3aa5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('goal', sa.Column('title', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('goal', 'title')
    # ### end Alembic commands ###
