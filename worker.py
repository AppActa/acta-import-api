from redis import Redis
from rq import SpawnWorker

from app.database.redis import get_pool
from app.services.fila import fila_uploads


if __name__ == '__main__':
    SpawnWorker([fila_uploads], connection=Redis(connection_pool=get_pool())).work()
