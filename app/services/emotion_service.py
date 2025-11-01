import uuid
import cv2
from fer.fer import FER
from app.db.database import SessionLocal
from app.models.emotion import Emotion
from app.models.emotion_type import EmotionType
from app.types.modality_enum import ModalityEnum
from app.utils.base64 import base64_to_image
from app.types.emotions_request import EmotionRequest
from app.types.emotions_response import EmotionResponse
from sqlalchemy.exc import SQLAlchemyError


class EmotionService:
    def __init__(self):
        # Desativa MTCNN para evitar erro de GPU (usa dlib, CPU only)
        self._detector = FER(mtcnn=False)

    def process_emotion(self, data: EmotionRequest) -> EmotionResponse:
        db = SessionLocal()
        try:
            user_id = data.get("correlation_id", None)
            timestamp = data.get("timestamp", None)
            frame = data.get("frame", None)

            if not frame:
                raise ValueError("Frame (base64) não fornecido.")

            image = base64_to_image(frame)

            # Garante que a imagem esteja em formato RGB (3 canais)
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:  # RGBA
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

            # Detecta emoções
            emotions = self._detector.detect_emotions(image)

            # Caso nenhuma emoção seja detectada → retorna unknown e NÃO salva
            if not emotions:
                res = EmotionResponse(
                    user_id=user_id,
                    timestamp=timestamp,
                    emotion="unknown",
                    confidence=0.0
                )
                return res.model_dump_json()

            # Extrai emoções detectadas (primeiro rosto)
            emotion_response = emotions[0].get("emotions", {})
            dominant_emotion = max(emotion_response, key=emotion_response.get)
            confidence_score = emotion_response[dominant_emotion]

            response = EmotionResponse(
                user_id=user_id,
                timestamp=timestamp,
                emotion=dominant_emotion,
                confidence=confidence_score
            )

            # Valida campos obrigatórios
            if not user_id or not timestamp:
                raise ValueError("Campos obrigatórios ausentes: user_id e timestamp.")

            # Busca o tipo de emoção
            emotion_type = db.query(EmotionType).filter_by(name=dominant_emotion).first()
            if not emotion_type:
                raise ValueError(f"Tipo de emoção '{dominant_emotion}' não encontrado na tabela emotions_type.")

            # Cria registro no banco
            emotion_entry = Emotion(
                id=uuid.uuid4(),
                modality=ModalityEnum.video,
                emotion_type_id=emotion_type.id,
                confidence=confidence_score,
                timestamp=timestamp,
                user_id=user_id
            )

            db.add(emotion_entry)
            db.commit()
            db.refresh(emotion_entry)

            return response.model_dump_json()

        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Database error: {str(e)}")

        except Exception as e:
            raise Exception(f"Error processing emotion: {str(e)}")

        finally:
            db.close()
