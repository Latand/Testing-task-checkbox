"""remove some constraints

Revision ID: 8bf4be2f1aa6
Revises: 0dc01a31b63a
Create Date: 2024-05-01 10:52:24.548763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bf4be2f1aa6'
down_revision: Union[str, None] = '0dc01a31b63a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('receiptitems', 'comment',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('receiptitems', 'comment',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
