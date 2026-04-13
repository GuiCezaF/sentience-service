import asyncio
import json
from app.core.redis import redis, REDIS_LIST, REDIS_CHANNEL
from app.services.emotion_service import EmotionService


async def consume_frames():
    """Async loop that consumes frames from the Redis list and publishes results to the Pub/Sub channel."""
    # Safety check: Wait for Redis connection
    while True:
        try:
            await redis.ping()
            print("[Redis] Connected successfully")
            break
        except Exception as e:
            print(f"[Redis] Waiting for connection: {e}")
            await asyncio.sleep(2)

    service = EmotionService()
    while True:
        try:
            frame = await redis.brpop(REDIS_LIST, timeout=5)
            if frame:
                _, payload = frame
                
                try:
                    data = json.loads(payload)
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    sample = payload[:20] if isinstance(payload, bytes) else str(payload)[:20]
                    print(f"[Redis] Error decoding payload: {e}. Start of payload: {sample}")
                    continue

                result = service.process_emotion(data)
                
                await redis.publish(REDIS_CHANNEL, result)

        except Exception as e:
            print(f"[FastAPI] Error in consumer loop: {e}")
            await asyncio.sleep(1)
