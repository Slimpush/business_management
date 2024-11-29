"""fix: ltree

Revision ID: 66e8af69bdfe
Revises: 52a0e206aa75
Create Date: 2024-11-27 18:05:15.662114

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "66e8af69bdfe"
down_revision: Union[str, None] = "52a0e206aa75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
