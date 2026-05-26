import time
import logging
from fastapi import Request
from app.db.redis_client import get_redis
from app.core.exceptions import AppException
from app.core.security import verify_firebase_token

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, limit: int, window: int, key_type: str = "ip"):
        """
        limit: Number of requests allowed in the window.
        window: Window size in seconds.
        key_type: "ip" or "user".
        """
        self.limit = limit
        self.window = window
        self.key_type = key_type

    async def __call__(self, request: Request):
        redis = get_redis()
        if not redis:
            logger.warning("Redis is not initialized or unavailable. Bypassing rate limiting.")
            return

        # Determine the unique key identifier
        identifier = None
        if self.key_type == "user":
            # Extract authorization token
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.lower().startswith("bearer "):
                raise AppException(status_code=401, message="Authorization header is required")
            
            token = auth_header.split(" ", 1)[1].strip()
            try:
                decoded = verify_firebase_token(token)
                identifier = decoded.get("uid")
            except Exception as e:
                logger.error(f"RateLimiter auth error: {e}")
                raise AppException(status_code=401, message="Invalid token")
        
        # If user identifier was not set (or key_type is "ip"), fallback to IP
        if not identifier:
            x_forwarded_for = request.headers.get("x-forwarded-for")
            if x_forwarded_for:
                identifier = x_forwarded_for.split(",")[0].strip()
            else:
                identifier = request.client.host if request.client else "unknown"

        # Unique key for Redis
        path = request.url.path
        key = f"ratelimit:{self.key_type}:{identifier}:{path}"

        try:
            current_time = time.time()
            clear_before = current_time - self.window

            # Use pipeline for atomic Redis operations
            async with redis.pipeline(transaction=True) as pipe:
                # Remove older requests from the sliding window
                pipe.zremrangebyscore(key, 0, clear_before)
                # Add current request timestamp
                pipe.zadd(key, {str(current_time): current_time})
                # Get the count of requests in the window
                pipe.zcard(key)
                # Set TTL on the key to clean up memory eventually
                pipe.expire(key, self.window + 10)
                
                # Execute pipeline
                _, _, count, _ = await pipe.execute()

            if count > self.limit:
                logger.warning(f"Rate limit exceeded for key {key} (count: {count}/{self.limit})")
                raise AppException(
                    status_code=429,
                    message=f"Too many requests. Limit is {self.limit} requests per {self.window} seconds."
                )

        except AppException:
            raise
        except Exception as e:
            logger.error(f"Rate limiter Redis error: {e}. Bypassing limit control.", exc_info=True)
            return
