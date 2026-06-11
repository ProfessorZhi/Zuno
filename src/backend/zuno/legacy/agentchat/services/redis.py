import pickle
from typing import Optional

import redis
from loguru import logger
from redis import ConnectionPool, RedisCluster

from agentchat.settings import app_settings


class RedisClient:
    def __init__(self, url: str | None = None, max_connections: int = 10):
        self.url = url
        self.max_connections = max_connections
        self.pool: ConnectionPool | None = None
        self.connection: redis.StrictRedis | RedisCluster | None = None

    def _resolve_url(self) -> str:
        endpoint = self.url or (app_settings.redis or {}).get("endpoint")
        if not endpoint:
            raise ValueError("redis endpoint is not configured")
        return endpoint

    def _connect(self):
        if self.connection is not None:
            return

        endpoint = self._resolve_url()
        if not isinstance(endpoint, str):
            raise ValueError("redis init only supports standalone mode")

        self.pool = ConnectionPool.from_url(endpoint, max_connections=self.max_connections)
        self.connection = redis.StrictRedis(connection_pool=self.pool)

    def setNx(self, key, value, expiration=3600):
        self._connect()
        try:
            if pickled := pickle.dumps(value):
                result = self.connection.setnx(key, pickled)
                self.connection.expire(key, expiration)
                return bool(result)
            return False
        except TypeError as exc:
            raise TypeError("RedisCache only accepts values that can be pickled.") from exc
        finally:
            self.close()

    def set(self, key, value, expiration=3600):
        self._connect()
        try:
            if pickled := pickle.dumps(value):
                result = self.connection.setex(key, expiration, pickled)
                if not result:
                    raise ValueError("redis could not set value")
            else:
                logger.error("pickle error, value={}", value)
        except TypeError as exc:
            raise TypeError("RedisCache only accepts values that can be pickled.") from exc
        finally:
            self.close()

    def hsetkey(self, name, key, value, expiration=3600):
        self._connect()
        try:
            result = self.connection.hset(name, key, value)
            if expiration:
                self.connection.expire(name, expiration)
            return result
        finally:
            self.close()

    def hset(
        self,
        name,
        key: Optional[str] = None,
        value: Optional[str] = None,
        mapping: Optional[dict] = None,
        items: Optional[list] = None,
        expiration: int = 3600,
    ):
        self._connect()
        try:
            result = self.connection.hset(name, key, value, mapping, items)
            if expiration:
                self.connection.expire(name, expiration)
            return result
        finally:
            self.close()

    def hget(self, name, key):
        self._connect()
        try:
            return self.connection.hget(name, key)
        finally:
            self.close()

    def hgetall(self, name):
        self._connect()
        try:
            return self.connection.hgetall(name)
        finally:
            self.close()

    def delete(self, key):
        self._connect()
        try:
            return self.connection.delete(key)
        finally:
            self.close()

    def get(self, key):
        self._connect()
        try:
            value = self.connection.get(key)
            return pickle.loads(value) if value else None
        finally:
            self.close()

    def incr(self, key, expiration=3600):
        self._connect()
        try:
            value = self.connection.incr(key)
            if expiration:
                self.connection.expire(key, expiration)
            return value
        finally:
            self.close()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None


redis_client = RedisClient()
