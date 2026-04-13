import pytest
import sys
from unittest.mock import MagicMock, AsyncMock

# We mock external libraries before any 'app' imports to prevent side effects at import time.
import redis.asyncio as aioredis
import sqlalchemy
import cv2
import onnxruntime as ort

# Mock Redis from_url
_mock_redis_client = AsyncMock()
aioredis.from_url = MagicMock(return_value=_mock_redis_client)

# Mock SQLAlchemy create_engine
_mock_engine = MagicMock()
sqlalchemy.create_engine = MagicMock(return_value=_mock_engine)

# Mock OpenCV CascadeClassifier
cv2.CascadeClassifier = MagicMock()

# Mock ONNX Runtime session
_mock_ort_session = MagicMock()
_mock_ort_session.get_inputs.return_value = [MagicMock(name="input")]
ort.InferenceSession = MagicMock(return_value=_mock_ort_session)
# ---------------------------

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def mock_db_session(mocker):
    """Mock for SQLAlchemy database session."""
    mock = MagicMock()
    # Patch the SessionLocal in the service
    mocker.patch("app.services.emotion_service.SessionLocal", return_value=mock)
    return mock

@pytest.fixture
def mock_redis():
    """Returns the shared mock redis client and resets it."""
    _mock_redis_client.reset_mock()
    return _mock_redis_client

@pytest.fixture
def mock_inference_session():
    """Returns the shared mock ONNX session and resets it."""
    import numpy as np
    _mock_ort_session.reset_mock()
    dummy_output = np.array([[0.1, 0.05, 0.05, 0.5, 0.1, 0.1, 0.1]]) # 'happy' is index 3
    _mock_ort_session.run.return_value = [dummy_output]
    return _mock_ort_session
