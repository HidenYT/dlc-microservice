"""Removed sent_back flag from results model

Revision ID: 42dfe4ddb26b
Revises: dabaefb42760
Create Date: 2024-04-17 12:17:58.779952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42dfe4ddb26b'
down_revision = 'dabaefb42760'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inference_results', schema=None) as batch_op:
        batch_op.drop_column('sent_back')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inference_results', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sent_back', sa.BOOLEAN(), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
