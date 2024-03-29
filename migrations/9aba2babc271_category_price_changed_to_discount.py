"""Category price changed to discount

Revision ID: 9aba2babc271
Revises: 8c6e0b6a9f84
Create Date: 2020-01-30 20:54:45.558947

"""
from alembic import op
import sqlalchemy as sa
import backend
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9aba2babc271'
down_revision = '8c6e0b6a9f84'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('discount', sa.Float(), nullable=True))
    op.drop_column('category', 'price')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.drop_column('category', 'discount')
    # ### end Alembic commands ###
