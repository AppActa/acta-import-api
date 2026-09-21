from contextlib import contextmanager
from fastapi import HTTPException
from dotenv import load_dotenv
from os import getenv
from psycopg2 import connect

load_dotenv()

DB_URL = getenv('DB_URL')

def _conectar():
    return connect(DB_URL)

def get_conn():
    try:
       conn = _conectar()
    except Exception:
        raise HTTPException(status_code=503, detail='Erro no banco de dados')
    
    try:
        yield conn
    finally:
        conn.close()

@contextmanager # permite usar def com with
def conn_worker():
    conn = _conectar()

    try:
        yield conn
    finally:
        conn.close()