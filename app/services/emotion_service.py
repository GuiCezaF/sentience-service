import uuid
import cv2
import numpy as np
import onnxruntime as ort
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import SessionLocal
from app.models.emotion import Emotion
from app.models.emotion_type import EmotionType
from app.settings import EMOTION_MODEL_PATH
from app.types.emotions_request import EmotionRequest
from app.types.emotions_response import EmotionResponse
from app.types.modality_enum import ModalityEnum
from app.utils.base64 import base64_to_image

EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]


class EmotionService:
    def __init__(self):
        self._session = ort.InferenceSession(
            EMOTION_MODEL_PATH,
            providers=["CPUExecutionProvider"],
        )
        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def process_emotion(self, data: EmotionRequest) -> str:
        db = SessionLocal()
        try:
            user_id = data.correlation_id if hasattr(data, "correlation_id") else data.get("correlation_id")
            timestamp = data.timestamp if hasattr(data, "timestamp") else data.get("timestamp")
            frame = data.frame if hasattr(data, "frame") else data.get("frame")

            if not frame:
                raise ValueError("Frame (base64) not provided.")

            image = base64_to_image(frame)
            face = self._detect_face(image)

            if face is None:
                return EmotionResponse(
                    user_id=user_id,
                    timestamp=timestamp,
                    emotion="unknown",
                    confidence=0.0,
                ).model_dump_json()

            dominant_emotion, confidence_score = self._predict(face)

            response = EmotionResponse(
                user_id=user_id,
                timestamp=timestamp,
                emotion=dominant_emotion,
                confidence=confidence_score,
            )

            if not user_id or not timestamp:
                raise ValueError("Missing required fields: user_id and timestamp.")

            emotion_type = db.query(EmotionType).filter_by(name=dominant_emotion).first()
            if not emotion_type:
                raise ValueError(f"Emotion type '{dominant_emotion}' not found in emotion_types table.")

            emotion_entry = Emotion(
                id=uuid.uuid4(),
                modality=ModalityEnum.video,
                emotion_type_id=emotion_type.id,
                confidence=confidence_score,
                timestamp=timestamp,
                user_id=user_id,
            )

            db.add(emotion_entry)
            db.commit()
            db.refresh(emotion_entry)

            return response.model_dump_json()

        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Database error: {str(e)}") from e

        except Exception as e:
            raise Exception(f"Error processing emotion: {str(e)}") from e

        finally:
            db.close()

    def _detect_face(self, image: np.ndarray) -> np.ndarray | None:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        faces = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        if len(faces) == 0:
            return None

        x, y, w, h = faces[0]
        face_crop = gray[y : y + h, x : x + w]
        return cv2.resize(face_crop, (48, 48))

    def _predict(self, face: np.ndarray) -> tuple[str, float]:
        tensor = face.astype(np.float32) / 255.0
        tensor = tensor[np.newaxis, np.newaxis, :, :]  # (1, 1, 48, 48)

        input_name = self._session.get_inputs()[0].name
        outputs = self._session.run(None, {input_name: tensor})[0][0]

        exp = np.exp(outputs - np.max(outputs))
        probabilities = exp / exp.sum()

        idx = int(np.argmax(probabilities))
        return EMOTION_LABELS[idx], float(probabilities[idx])
