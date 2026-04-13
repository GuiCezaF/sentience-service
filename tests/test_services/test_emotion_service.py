import json
import pytest
import numpy as np
from datetime import datetime
from uuid import uuid4
from unittest.mock import MagicMock
from app.services.emotion_service import EmotionService

@pytest.fixture
def service(mock_inference_session):
    """EmotionService instance with mocked inference."""
    return EmotionService()

def test_process_emotion_success(service, mock_db_session, mocker):
    """
    Test Case: Success
    Verify that an emotion is processed and saved when a face is detected.
    """
    # Arrange
    timestamp = datetime.now()
    user_id = str(uuid4())
    data = {
        "correlation_id": user_id,
        "timestamp": timestamp,
        "frame": "dummy_base64"
    }
    
    # Mock base64_to_image to return a dummy image
    mocker.patch("app.services.emotion_service.base64_to_image", return_value=np.zeros((100, 100, 3), dtype=np.uint8))
    
    # Mock face detection to return one face
    service._face_cascade.detectMultiScale = MagicMock(return_value=[(10, 10, 50, 50)])
    
    # Mock DB query for EmotionType
    mock_emotion_type = MagicMock()
    mock_emotion_type.id = uuid4()
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_emotion_type

    # Act
    result_json = service.process_emotion(data)
    result = json.loads(result_json)

    # Assert
    assert result["user_id"] == user_id
    assert result["emotion"] == "happy" 
    # The mock value 0.5 after Softmax results in ~0.20
    assert result["confidence"] > 0.20
    assert result["confidence"] < 0.21
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_process_emotion_no_face(service, mocker):
    """
    Test Case: Success (No Face)
    Verify that it returns 'unknown' when no face is detected.
    """
    # Arrange
    mocker.patch("app.services.emotion_service.base64_to_image", return_value=np.zeros((100, 100, 3), dtype=np.uint8))
    service._face_cascade.detectMultiScale = MagicMock(return_value=[])
    
    data = {
        "correlation_id": str(uuid4()),
        "timestamp": datetime.now(),
        "frame": "dummy_base64"
    }

    # Act
    result_json = service.process_emotion(data)
    result = json.loads(result_json)

    # Assert
    assert result["emotion"] == "unknown"
    assert result["confidence"] == 0.0

def test_process_emotion_missing_frame(service):
    """
    Test Case: Error
    Verify that it raises ValueError when frame is missing.
    """
    data = {"correlation_id": "123", "timestamp": datetime.now()}
    
    with pytest.raises(Exception) as exc:
        service.process_emotion(data)
    assert "Frame (base64) not provided" in str(exc.value)

def test_process_emotion_db_error(service, mock_db_session, mocker):
    """
    Test Case: Error (Database)
    Verify that database errors are caught and rolled back.
    """
    # Arrange
    mocker.patch("app.services.emotion_service.base64_to_image", return_value=np.zeros((100, 100, 3), dtype=np.uint8))
    service._face_cascade.detectMultiScale = MagicMock(return_value=[(10, 10, 50, 50)])
    
    # Mock DB to raise SQLAlchemyError on commit
    from sqlalchemy.exc import SQLAlchemyError
    mock_db_session.commit.side_effect = SQLAlchemyError("DB Fail")
    
    mock_emotion_type = MagicMock()
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_emotion_type

    data = {
        "correlation_id": str(uuid4()),
        "timestamp": datetime.now(),
        "frame": "dummy_base64"
    }

    # Act & Assert
    with pytest.raises(Exception) as exc:
        service.process_emotion(data)
    
    assert "Database error" in str(exc.value)
    mock_db_session.rollback.assert_called_once()
