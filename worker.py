from redis import Redis
from rq import SimpleWorker
from rq.timeouts import TimerDeathPenalty
from app.database.redis import get_pool
from app.services.fila import fila_uploads

# timeout adaptado para windows
class WindowsSimpleWorker(SimpleWorker):
    death_penalty_class = TimerDeathPenalty

if __name__ == '__main__':
    WindowsSimpleWorker([fila_uploads], connection=Redis(connection_pool=get_pool()),).work()