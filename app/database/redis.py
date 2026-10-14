from fastapi import HTTPException
from redis import Redis, ConnectionPool, SSLConnection
from redis.exceptions import RedisError
from functools import lru_cache
from app.config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_SSL

@lru_cache # apenas um pool por sessão
def get_pool() -> ConnectionPool:
    pool_options = {'host': REDIS_HOST, 'port': REDIS_PORT, 'db': REDIS_DB, 'password': REDIS_PASSWORD, 'max_connections': 20, 'retry_on_timeout': True}
    if REDIS_SSL:
        pool_options['connection_class'] = SSLConnection
    return ConnectionPool(**pool_options)

def get_conn() -> Redis:
    try:
        return Redis(connection_pool=get_pool())
    except RedisError as re:
        raise HTTPException(status_code=503, detail='Redis indisponível')