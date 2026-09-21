from rq import Queue
from redis import Redis
from app.database.redis import get_pool

conn = Redis(connection_pool=get_pool())

# 5 minutos de tolerância do job
fila_uploads = Queue('uploads', connection=conn, default_timeout=300)