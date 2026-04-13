import json
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from app.core.consumer import consume_frames

@pytest.mark.asyncio
async def test_consume_frames_success(mock_redis, mocker):
    """
    Test Case: Success
    Verify that the consumer reads from Redis, processes the frame, and publishes the result.
    """
    # Arrange
    payload = {
        "correlation_id": "user-123",
        "timestamp": "2024-03-20T10:00:00",
        "frame": "base64_data"
    }
    # mock brpop return (key, value)
    mock_redis.brpop = AsyncMock(side_effect=[("emotion_frames", json.dumps(payload)), Exception("Stop loop")])
    mock_redis.publish = AsyncMock()
    
    # Mock EmotionService.process_emotion
    mock_service = MagicMock()
    mock_service.process_emotion.return_value = json.dumps({"status": "processed"})
    mocker.patch("app.core.consumer.EmotionService", return_value=mock_service)

    # Act
    # Use wait_for to prevent hanging due to the while True loop in consume_frames.
    # The loop will process the first payload, then hit the exception, log it, sleep 1s, and retry.
    # We only need to verify it processed the first one.
    task = asyncio.create_task(consume_frames())
    await asyncio.sleep(0.1) # Give it time to process
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Assert
    mock_redis.brpop.assert_called()
    mock_service.process_emotion.assert_called_once_with(payload)
    mock_redis.publish.assert_called_once_with("emotion_results", json.dumps({"status": "processed"}))

@pytest.mark.asyncio
async def test_consume_frames_invalid_json(mock_redis, mocker):
    """
    Test Case: Error
    Verify that the consumer handles invalid JSON payloads without crashing.
    """
    # Arrange
    mock_redis.brpop = AsyncMock(side_effect=[("emotion_frames", "invalid-json"), Exception("Stop loop")])
    mock_redis.publish = AsyncMock()
    
    # Spy on print to verify error logging
    spy_print = mocker.patch("builtins.print")

    # Act
    task = asyncio.create_task(consume_frames())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Assert
    spy_print.assert_called()
    assert "[FastAPI] Error consuming frame" in spy_print.call_args[0][0]
    mock_redis.publish.assert_not_called()
