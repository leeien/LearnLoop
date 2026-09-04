import json
import logging
from dataclasses import dataclass
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    count: int
    retry_after: int
    redis_available: bool


class RedisClient:
    _INCR_WITH_EXPIRE_SCRIPT = """
    local current = redis.call('INCR', KEYS[1])
    if current == 1 then
        redis.call('EXPIRE', KEYS[1], ARGV[1])
    end
    local ttl = redis.call('TTL', KEYS[1])
    return {current, ttl}
    """

    def __init__(self, url: str) -> None:
        self._client = Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=0.3,
            socket_timeout=0.5,
            retry_on_timeout=False,
        )

    def get_json(self, key: str) -> Any | None:
        try:
            value = self._client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (RedisError, OSError, ValueError, TypeError) as error:
            self._log_fallback(error)
            return None

    def set_json(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
    ) -> bool:
        try:
            payload = json.dumps(
                value,
                ensure_ascii=False,
                default=str,
            )
            if ttl_seconds is None:
                self._client.set(key, payload)
            else:
                self._client.setex(key, ttl_seconds, payload)
            return True
        except (RedisError, OSError, TypeError, ValueError) as error:
            self._log_fallback(error)
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self._client.delete(key))
        except (RedisError, OSError) as error:
            self._log_fallback(error)
            return False

    def exists(self, key: str) -> bool:
        try:
            return bool(self._client.exists(key))
        except (RedisError, OSError) as error:
            self._log_fallback(error)
            return False

    def incr_with_expire(
        self,
        key: str,
        expire_seconds: int,
    ) -> tuple[int, int] | None:
        try:
            result = self._client.eval(
                self._INCR_WITH_EXPIRE_SCRIPT,
                1,
                key,
                expire_seconds,
            )
            return int(result[0]), max(0, int(result[1]))
        except (RedisError, OSError, TypeError, ValueError) as error:
            self._log_fallback(error)
            return None

    def rate_limit_check(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        result = self.incr_with_expire(key, window_seconds)
        if result is None:
            return RateLimitResult(
                allowed=True,
                count=0,
                retry_after=0,
                redis_available=False,
            )
        count, ttl = result
        return RateLimitResult(
            allowed=count <= limit,
            count=count,
            retry_after=ttl,
            redis_available=True,
        )

    @staticmethod
    def _log_fallback(error: Exception) -> None:
        logger.debug("Redis unavailable; using fallback: %s", error)


redis_client = RedisClient(get_settings().redis_url)


def get_json(key: str) -> Any | None:
    return redis_client.get_json(key)


def set_json(
    key: str,
    value: Any,
    ttl_seconds: int | None = None,
) -> bool:
    return redis_client.set_json(key, value, ttl_seconds)


def delete(key: str) -> bool:
    return redis_client.delete(key)


def exists(key: str) -> bool:
    return redis_client.exists(key)


def incr_with_expire(
    key: str,
    expire_seconds: int,
) -> tuple[int, int] | None:
    return redis_client.incr_with_expire(key, expire_seconds)


def rate_limit_check(
    key: str,
    limit: int = 10,
    window_seconds: int = 60,
) -> RateLimitResult:
    return redis_client.rate_limit_check(key, limit, window_seconds)

