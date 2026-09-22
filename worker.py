from redis import Redis
from rq import Worker

from app.database.redis import get_pool
from app.services.fila import fila_uploads


if __name__ == '__main__':
    Worker([fila_uploads], connection=Redis(connection_pool=get_pool())).work()