"""empty message

Revision ID: 659c3016d23d
Revises: 9e3d918ea693
Create Date: 2021-10-29 00:33:10.495256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '659c3016d23d'
down_revision = '9e3d918ea693'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goals',
    sa.Column('goal_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('goal_id')
    )
    op.drop_table('goal')
    op.add_column('tasks', sa.Column('goal_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tasks', 'goals', ['goal_id'], ['goal_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'goal_id')
    op.create_table('goal',
    sa.Column('goal_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('goal_id', name='goal_pkey')
    )
    op.drop_table('goals')
    # ### end Alembic commands ###
