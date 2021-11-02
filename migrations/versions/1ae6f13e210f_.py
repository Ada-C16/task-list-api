"""empty message

Revision ID: 1ae6f13e210f
Revises: 658c883b5a8e
Create Date: 2021-11-01 15:07:11.280721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ae6f13e210f'
down_revision = '658c883b5a8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('fk_goal_id', sa.Integer(), nullable=True))
    op.drop_constraint('task_goal_id_fkey', 'task', type_='foreignkey')
    op.create_foreign_key(None, 'task', 'goal', ['fk_goal_id'], ['goal_id'])
    op.drop_column('task', 'goal_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('goal_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.create_foreign_key('task_goal_id_fkey', 'task', 'goal', ['goal_id'], ['goal_id'])
    op.drop_column('task', 'fk_goal_id')
    # ### end Alembic commands ###
