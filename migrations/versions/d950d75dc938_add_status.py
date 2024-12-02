"""add status

Revision ID: d950d75dc938
Revises: 6f2196d55316
Create Date: 2024-11-30 16:22:50.094520

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = "d950d75dc938"
down_revision: Union[str, None] = "6f2196d55316"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Определяем ENUM для статуса задач
task_status_enum = ENUM(
    "NEW", "IN PROGRESS", "DONE", "CANCELED", name="taskstatus", schema=None
)

# Имя таблицы
table_name = "tasks"


def upgrade():
    # Получаем соединение с базой данных
    bind = op.get_bind()

    # Проверяем существование типа taskstatus
    result = bind.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'taskstatus';")
    ).fetchone()

    # Если типа нет, создаем его
    if not result:
        task_status_enum.create(bind, checkfirst=True)

    # Проверяем существование столбца status
    result = bind.execute(
        sa.text(
            f"SELECT 1 FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='status';"
        )
    ).fetchone()

    # Если столбца нет, добавляем его
    if not result:
        op.add_column(
            table_name,
            sa.Column("status", task_status_enum, nullable=False, server_default="NEW"),
        )


def downgrade():
    # Получаем соединение с базой данных
    bind = op.get_bind()

    # Проверяем существование столбца status
    result = bind.execute(
        sa.text(
            f"SELECT 1 FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='status';"
        )
    ).fetchone()

    # Если столбец существует, удаляем его
    if result:
        op.drop_column(table_name, "status")

    # Проверяем существование типа taskstatus
    result = bind.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'taskstatus';")
    ).fetchone()

    # Если тип существует, удаляем его
    if result:
        task_status_enum.drop(bind, checkfirst=True)
