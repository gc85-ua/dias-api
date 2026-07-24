import logging
import redis
from app.core.config import Settings
from app.core.config import settings as default_settings


class CacheDAO:
    def __init__(self, settings: Settings):
        host = settings.cache_db_host
        port = settings.cache_db_port
        try:
            self.client = redis.Redis(host=host, port=port, db=settings.cache_db)
        except Exception as e:
            logging.error(f"Error occurred while connecting to cache: {e}")

    # set and get operations are abstrated from the client connection to allow for easier db separation in the future if needed.
    # This also makes testing and mocking easier.

    def _set(
        self,
        client: redis.Redis,
        key: str,
        value: dict | str | float,
        ttl: int,
    ):
        try:
            client.set(key, value, ex=ttl)
        except Exception as e:
            logging.error(f"Error occurred while setting cache: {e}")

    def _get(self, client: redis.Redis, key: str) -> dict | str | float | None:
        value = None
        try:
            value = client.get(key)
            if value is not None:
                return value
        except Exception as e:
            logging.error(f"Error occurred while getting cache: {e}")

        return value

    def set_cache(self, key: str, value: dict | str | float, ttl: int = 86400):
        self._set(self.client, key, value, ttl)

    def get_cache(self, key: str) -> dict | str | float | None:
        return self._get(self.client, key)


# export as a singleton instance
cache_client = CacheDAO(settings=default_settings)
