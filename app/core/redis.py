from app.settings import envs
import redis.asyncio as aioredis

# Single shared connection for the entire app
REDIS_URL = envs("REDIS_URL", default="redis://redis:6379")
redis = aioredis.from_url(REDIS_URL, decode_responses=True)

REDIS_LIST = "emotion_frames"
REDIS_CHANNEL = "emotion_results"
