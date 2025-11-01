"""removendo fk do usuario na emocao

Revision ID: 1fb5bd7fa7c7
Revises: f952aa0f0d04
Create Date: 2025-11-01 19:50:13.285363
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fb5bd7fa7c7'
down_revision: Union[str, Sequence[str], None] = 'f952aa0f0d04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Remover a foreign key que referenciava users.id
    op.drop_constraint('emotions_user_id_fkey', 'emotions', type_='foreignkey')

    # Alterar o tipo da coluna user_id (opcional, só se quiser)
    op.alter_column(
        'emotions', 'user_id',
        existing_type=sa.UUID(),
        type_=sa.String(length=255),
        existing_nullable=True
    )


def downgrade():
    # Reverter o tipo da coluna (mantém sem FK)
    op.alter_column(
        'emotions', 'user_id',
        existing_type=sa.String(length=255),
        type_=sa.UUID(),
        existing_nullable=True
    )
