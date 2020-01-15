"""NodeTree changed to Adjacency list

Revision ID: 42d7fa594797
Revises: 34e80cdcadd0
Create Date: 2020-01-15 20:48:03.849873

"""
from alembic import op
import sqlalchemy as sa
import backend
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '42d7fa594797'
down_revision = '34e80cdcadd0'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('created_at', backend.database.types.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', backend.database.types.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=True),
    sa.Column('public', sa.Boolean(name='public'), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('tree_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=True),
    sa.Column('lft', sa.Integer(), nullable=False),
    sa.Column('rgt', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['category.id'], name=op.f('fk_category_parent_id_category'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_category'))
    )
    op.create_table('image',
    sa.Column('id', sa.BigInteger().with_variant(sa.INTEGER(), 'sqlite'), nullable=False),
    sa.Column('created_at', backend.database.types.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', backend.database.types.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('path', sa.String(length=128), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('category_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], name=op.f('fk_image_category_id_category')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_image'))
    )
    op.drop_table('photo_node')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('photo_node',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('path', sqlalchemy_utils.types.ltree.LtreeType(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('folder', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('public', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('image', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_photo_node')
    )
    op.drop_table('image')
    op.drop_table('category')
    # ### end Alembic commands ###
