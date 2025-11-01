import uuid
import enum
from sqlalchemy import Column, ForeignKey, String, Float, DateTime, Enum, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

from app.models.user import User
from app.types.modality_enum import ModalityEnum 

class Emotion(Base):
    __tablename__ = "emotions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    modality = Column(Enum(ModalityEnum, name="modality"), nullable=False)

    user_id = Column(String(255), nullable=False)

    # Referência ao tipo de emoção
    emotion_type_id = Column(UUID(as_uuid=True), ForeignKey("emotion_types.id"), nullable=False)
    emotion_type = relationship("EmotionType", back_populates="emotions")

    confidence = Column(Float, nullable=False)     # Ex: 0.95
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
