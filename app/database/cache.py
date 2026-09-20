import logging

import redis

from app.core.config import Settings
from app.core.config import settings as default_settings

logger = logging.getLogger(__name__)

class CacheDAO:
    def __init__(self, settings: Settings):
        host = settings.cache_db_host
        port = settings.cache_db_port
        try:
            self.client_connection = redis.Redis(host=host, port=port, db=settings.cache_db)
        except redis.RedisError as e:
            logger.error("Error occurred while connecting to cache", extra={"event_name": "cache.connection_error", "error": str(e)})
            self.client_connection = None

    def _set(
        self,
        client: redis.Redis,
        key: str,
        value: dict | str | float,
        ttl: int,
    ) -> bool:
        try:
            client.set(key, value, ex=ttl)
            return True
        except redis.RedisError as e:
            logger.error("Error occurred while setting cache", extra={"event_name": "cache.set_error", "key": key, "error": str(e)})
            return False

    def _get(self, client: redis.Redis, key: str) -> dict | str | float | None:
        value = None
        try:
            value = client.get(key)
            if value is not None:
                return value
        except redis.RedisError as e:
            logger.error("Error occurred while getting cache", extra={"event_name": "cache.get_error", "key": key, "error": str(e)})

        return value

    def set_cache(self, key: str, value: dict | str | float, ttl: int = 86400) -> bool:
        if self.client_connection is None:
            logger.error("Cache client connection is not initialized", extra={"event_name": "cache.not_initialized"})
            return False
        return self._set(self.client_connection, key, value, ttl)

    def get_cache(self, key: str) -> dict | str | float | None:
        if self.client_connection is None:
            logger.error("Cache client connection is not initialized", extra={"event_name": "cache.not_initialized"})
            return None
        return self._get(self.client_connection, key)


# export as a singleton instance
cache_client = CacheDAO(settings=default_settings)
