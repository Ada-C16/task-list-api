"""adds Task model

Revision ID: 9823bd254953
Revises: 
Create Date: 2021-10-29 11:51:26.504155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9823bd254953'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goal',
    sa.Column('goal_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('goal_id')
    )
    op.create_table('task',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('task_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task')
    op.drop_table('goal')
    # ### end Alembic commands ###
