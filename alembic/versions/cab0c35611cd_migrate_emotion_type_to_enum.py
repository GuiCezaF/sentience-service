"""migrate_emotion_type_to_enum

Revision ID: cab0c35611cd
Revises: 9812001bd42e
Create Date: 2026-04-13 18:53:23.603232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'cab0c35611cd'
down_revision: Union[str, Sequence[str], None] = '9812001bd42e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Criar o tipo ENUM no PostgreSQL explicitamente
    emotion_type_enum = postgresql.ENUM('angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise', name='emotion_type_enum')
    emotion_type_enum.create(op.get_bind())

    # 2. Remover a constraint de foreign key primeiro
    op.drop_constraint('emotions_emotion_type_id_fkey', 'emotions', type_='foreignkey')
    
    # 3. Adicionar a nova coluna usando o tipo ENUM criado
    op.add_column('emotions', sa.Column('emotion_type', sa.Enum('angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise', name='emotion_type_enum'), nullable=False))
    
    # 4. Remover a coluna antiga
    op.drop_column('emotions', 'emotion_type_id')
    
    # 5. Excluir a tabela que não é mais necessária
    op.drop_table('emotion_types')


def downgrade() -> None:
    # 1. Recriar a tabela emotion_types
    op.create_table('emotion_types',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('emotion_types_pkey')),
    sa.UniqueConstraint('name', name=op.f('emotion_types_name_key'))
    )

    # 2. Readicionar a coluna de ID
    op.add_column('emotions', sa.Column('emotion_type_id', sa.UUID(), autoincrement=False, nullable=False))
    
    # 3. Restaurar a Foreign Key
    op.create_foreign_key('emotions_emotion_type_id_fkey', 'emotions', 'emotion_types', ['emotion_type_id'], ['id'])
    
    # 4. Remover a coluna de Enum
    op.drop_column('emotions', 'emotion_type')
    
    # 5. Remover o tipo Enum do banco
    emotion_type_enum = postgresql.ENUM('angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise', name='emotion_type_enum')
    emotion_type_enum.drop(op.get_bind())
