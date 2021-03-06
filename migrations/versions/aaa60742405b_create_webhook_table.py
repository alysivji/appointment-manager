"""Create webhook table

Revision ID: aaa60742405b
Revises: a4bb2a1e0a24
Create Date: 2018-04-10 14:36:32.907893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aaa60742405b'
down_revision = 'a4bb2a1e0a24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('webhook',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('endpoint_url', sa.String(length=280), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhook_created'), 'webhook', ['created'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_webhook_created'), table_name='webhook')
    op.drop_table('webhook')
    # ### end Alembic commands ###
