"""Slug removed from album

Revision ID: 7f1c0274397e
Revises: 5e7c3dea509b
Create Date: 2020-01-02 09:50:16.361812

"""
from alembic import op
import sqlalchemy as sa
import backend


# revision identifiers, used by Alembic.
revision = '7f1c0274397e'
down_revision = '5e7c3dea509b'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('album', 'slug')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('album', sa.Column('slug', sa.VARCHAR(length=64), autoincrement=False, nullable=False))
    # ### end Alembic commands ###