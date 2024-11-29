"""fix: user-department relate

Revision ID: a8a33483796e
Revises: 66e8af69bdfe
Create Date: 2024-11-27 18:26:14.520753

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "a8a33483796e"
down_revision: Union[str, None] = "66e8af69bdfe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
