import uuid
import enum
from sqlalchemy import Column, ForeignKey, String, Float, DateTime, Enum, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

from app.models.user import User
from app.types.modality_enum import ModalityEnum

class EmotionType(Base):
    __tablename__ = "emotion_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(50), unique=True, nullable=False)  # Ex: "happy", "sad", "angry"
    description = Column(String(255), nullable=True)

    # Relationship with emotions
    emotions = relationship("Emotion", back_populates="emotion_type")

    def __repr__(self):
        return f"<EmotionType(name='{self.name}')>"