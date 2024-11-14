"""add method to recipe

Revision ID: a1de90521219
Revises: 68220aed94eb
Create Date: 2024-11-12 15:20:28.813782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1de90521219'
down_revision = '68220aed94eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.add_column(sa.Column('method', sa.String(length=1024), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.drop_column('method')

    # ### end Alembic commands ###