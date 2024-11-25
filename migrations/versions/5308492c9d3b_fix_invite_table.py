from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision: str = "5308492c9d3b"
down_revision: Union[str, None] = "75e14017cbe4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str, connection: Connection) -> bool:
    """Проверка наличия столбца в таблице."""
    inspector = inspect(connection)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def row_exists(table_name: str, condition: str, connection: Connection) -> bool:
    """Проверка наличия записи в таблице."""
    query = text(f"SELECT 1 FROM {table_name} WHERE {condition} LIMIT 1;")
    result = connection.execute(query).fetchone()
    return result is not None


def upgrade() -> None:
    conn = op.get_bind()

    # Убедимся, что запись с id=1 в таблице companies существует
    if not row_exists("companies", "id = 1", conn):
        conn.execute(
            text(
                """
            INSERT INTO companies (id, name)
            VALUES (1, 'Default Company')
            ON CONFLICT (id) DO NOTHING;
        """
            )
        )

    # Проверяем наличие столбца company_id в таблице invite
    if not column_exists("invite", "company_id", conn):
        with op.batch_alter_table("invite", schema=None) as batch_op:
            batch_op.add_column(sa.Column("company_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_invite_company_id",
                "companies",
                ["company_id"],
                ["id"],
            )

    # Установим company_id для всех существующих записей
    conn.execute(text("UPDATE invite SET company_id = 1"))

    # Делаем столбец company_id NOT NULL
    with op.batch_alter_table("invite", schema=None) as batch_op:
        batch_op.alter_column("company_id", nullable=False)


def downgrade() -> None:
    conn = op.get_bind()

    # Проверяем, существует ли ограничение внешнего ключа перед удалением
    result = conn.execute(
        text(
            """
            SELECT conname
            FROM pg_constraint
            WHERE conname = 'fk_invite_company_id'
        """
        )
    ).fetchone()

    # Удаляем ограничение, если оно существует
    if result:
        with op.batch_alter_table("invite", schema=None) as batch_op:
            batch_op.drop_constraint("fk_invite_company_id", type_="foreignkey")

    # Удаляем столбец company_id
    with op.batch_alter_table("invite", schema=None) as batch_op:
        batch_op.drop_column("company_id")
