import time
import redis
from fastapi import HTTPException
from app.settings import settings

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def rate_limit(client_id: str, limit_per_minute: int):
    now = int(time.time())
    key = f"rl:{client_id}:{now // 60}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 70)
    if count > limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
