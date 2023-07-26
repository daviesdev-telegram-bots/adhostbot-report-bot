"""Order details

Revision ID: 878b3ec06f27
Revises: 
Create Date: 2023-07-26 11:55:44.187820

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '878b3ec06f27'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product')
    op.add_column('order', sa.Column('value', sa.Integer(), nullable=True))
    op.add_column('order', sa.Column('social_media', sa.String(), nullable=True))
    op.add_column('order', sa.Column('report_type', sa.String(), nullable=True))
    op.add_column('order', sa.Column('link', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'link')
    op.drop_column('order', 'report_type')
    op.drop_column('order', 'social_media')
    op.drop_column('order', 'value')
    op.create_table('product',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='product_pkey')
    )
    # ### end Alembic commands ###
