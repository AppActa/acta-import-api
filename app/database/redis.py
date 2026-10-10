from fastapi import HTTPException
from redis import Redis, ConnectionPool
from redis.exceptions import RedisError
from dotenv import load_dotenv
from os import getenv
from functools import lru_cache
from redis.connection import SSLConnection

load_dotenv()

REDIS_HOST = getenv('REDIS_HOST')
REDIS_PORT = getenv('REDIS_PORT')
REDIS_DB = getenv('REDIS_DB')
REDIS_PASSWORD = getenv('REDIS_PASSWORD')
REDIS_USERNAME = getenv('REDIS_USERNAME')
REDIS_TLS = getenv('REDIS_TLS', 'false').strip().lower() == 'true'

@lru_cache # apenas um pool por sessão
def get_pool() -> ConnectionPool:
    # Usa ssl connection quando TLS foi habilitado
    connection_options = {'connection_class': SSLConnection} if REDIS_TLS else {}
    return ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, username=REDIS_USERNAME, password=REDIS_PASSWORD, max_connections=20, retry_on_timeout=True, **connection_options)

def get_conn() -> Redis:
    try:
        return Redis(connection_pool=get_pool())
    except RedisError as re:
        raise HTTPException(status_code=503, detail='Redis indisponível')
