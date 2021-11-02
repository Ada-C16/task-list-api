"""created FK in task.py

Revision ID: 49aeef97e604
Revises: 422f014a5e24
Create Date: 2021-10-30 16:41:41.963255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49aeef97e604'
down_revision = '422f014a5e24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('goal_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'task', 'goal', ['goal_id'], ['goal_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_column('task', 'goal_id')
    # ### end Alembic commands ###
