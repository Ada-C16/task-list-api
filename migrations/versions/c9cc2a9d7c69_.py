"""empty message

Revision ID: c9cc2a9d7c69
Revises: 8e83d753dd3f
Create Date: 2021-11-03 15:58:18.243130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9cc2a9d7c69'
down_revision = '8e83d753dd3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('task_goal_id_fkey', 'task', type_='foreignkey')
    op.create_foreign_key(None, 'task', 'goal', ['goal_id'], ['goal_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.create_foreign_key('task_goal_id_fkey', 'task', 'task', ['goal_id'], ['task_id'])
    # ### end Alembic commands ###
