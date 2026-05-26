import logging
from redis.asyncio import Redis, from_url

logger = logging.getLogger(__name__)

redis_client: Redis = None

async def init_redis(redis_url: str) -> Redis:
    global redis_client
    try:
        logger.info(f"Initializing Redis client with URL: {redis_url}")
        redis_client = from_url(redis_url, encoding="utf-8", decode_responses=True)
        # Test connection
        await redis_client.ping()  # type: ignore
        logger.info("Successfully connected to Redis.")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to initialize Redis client: {e}", exc_info=True)
        redis_client = None
        return None

async def close_redis():
    global redis_client
    if redis_client:
        logger.info("Closing Redis connection...")
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed.")

def get_redis() -> Redis:
    return redis_client
