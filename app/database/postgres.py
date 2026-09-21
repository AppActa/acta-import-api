from fastapi import HTTPException
from dotenv import load_dotenv
from os import getenv
from psycopg2 import connect

load_dotenv()

DB_URL = getenv('DB_URL')

def get_conn():
    conn = connect(DB_URL)
    
    try:
        yield conn
    except Exception as e:
        raise HTTPException(status_code=500, detail='Erro no banco de dados')
    finally:
        if conn is not None:
            conn.close()