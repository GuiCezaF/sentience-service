"""separando tipos de emocoes em outra tabela

Revision ID: 9812001bd42e
Revises: 1fb5bd7fa7c7
Create Date: 2025-11-01 20:04:30.484461

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '9812001bd42e'
down_revision: Union[str, Sequence[str], None] = '1fb5bd7fa7c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    # --- Criar tabela emotion_types se não existir ---
    if 'emotion_types' not in inspector.get_table_names():
        op.create_table(
            'emotion_types',
            sa.Column('id', sa.UUID(), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False, unique=True),
            sa.Column('description', sa.String(length=255), nullable=True)
        )

        # Inserir seed inicial
        emotions = [
            {"name": "sad", "description": "Expressão de tristeza"},
            {"name": "angry", "description": "Expressão de raiva"},
            {"name": "happy", "description": "Expressão de felicidade"},
            {"name": "fear", "description": "Expressão de medo"},
            {"name": "neutral", "description": "Expressão neutra"},
            {"name": "surprise", "description": "Expressão de surpresa"},
        ]

        for e in emotions:
            bind.execute(
                sa.text(
                    "INSERT INTO emotion_types (id, name, description) VALUES (:id, :name, :description)"
                ),
                {"id": str(uuid.uuid4()), "name": e["name"], "description": e["description"]}
            )

    # --- Alterar tabela emotions ---
    columns = [col["name"] for col in inspector.get_columns("emotions")]
    if "emotion_type_id" not in columns:
        op.add_column("emotions", sa.Column("emotion_type_id", sa.UUID(), nullable=False))
        op.create_foreign_key(
            None, "emotions", "emotion_types", ["emotion_type_id"], ["id"]
        )

    if "emotion" in columns:
        op.drop_column("emotions", "emotion")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col["name"] for col in inspector.get_columns("emotions")]
    if "emotion" not in columns:
        op.add_column(
            "emotions",
            sa.Column("emotion", sa.VARCHAR(length=20), autoincrement=False, nullable=False)
        )

    fks = [fk["name"] for fk in inspector.get_foreign_keys("emotions")]
    if fks:
        op.drop_constraint(fks[0], "emotions", type_="foreignkey")

    if "emotion_type_id" in columns:
        op.drop_column("emotions", "emotion_type_id")

    if "emotion_types" in inspector.get_table_names():
        op.drop_table("emotion_types")
