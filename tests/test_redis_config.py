import importlib

from redis.connection import SSLConnection

import app.database.redis as redis_database


def test_redis_tls_defaults_to_disabled_when_unset(monkeypatch):
    monkeypatch.delenv("REDIS_TLS", raising=False)

    module = importlib.reload(redis_database)

    assert module.REDIS_TLS is False


def test_redis_pool_uses_ssl_connection_when_tls_enabled(monkeypatch):
    monkeypatch.setattr(redis_database, "REDIS_HOST", "redis.example.test")
    monkeypatch.setattr(redis_database, "REDIS_PORT", "6379")
    monkeypatch.setattr(redis_database, "REDIS_DB", "0")
    monkeypatch.setattr(redis_database, "REDIS_USERNAME", "default")
    monkeypatch.setattr(redis_database, "REDIS_PASSWORD", "not-a-real-secret")
    monkeypatch.setattr(redis_database, "REDIS_TLS", True)
    redis_database.get_pool.cache_clear()

    try:
        pool = redis_database.get_pool()
        assert pool.connection_class is SSLConnection
        assert pool.connection_kwargs["username"] == "default"
    finally:
        redis_database.get_pool.cache_clear()
