from pymongo import MongoClient, ReturnDocument
from fastapi import HTTPException
from app.models.planilha import Planilha
from dotenv import load_dotenv
from os import getenv

# capturando informações do .env
load_dotenv()

# configurações de conexão com Mongo
MONGO_URL          = getenv('MONGO_URL')
DB_NAME            = getenv('DB_NAME')
COLLECTION_NAME    = 'planilhas'
COLLECTION_COUNTER = 'counter'

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
col_planilha = db[COLLECTION_NAME]
col_counter = db[COLLECTION_COUNTER]

# função para capturar próximo id
def get_next_id():
    contador = col_counter.find_one_and_update(
        {'_id': COLLECTION_NAME},
        {'$inc': {'id_inicial': 1}}, # id_inicial + 1
        upsert=True, # se não existir, criar
        return_document=ReturnDocument.AFTER # retorna documento após update
    )
    return contador['id_inicial']

# função para inserir planilha no banco
def inserir_planilha(planilha: Planilha, documentos) -> dict:
    try:
        if not documentos:
            raise HTTPException(status_code=400, detail='Arquivo vazio ou corrompido')
        
        # montando documento
        documento = {
            '_id': get_next_id(),
            'id_empresa': planilha.id_empresa,
            'id_ciclo': planilha.id_ciclo,
            'tipo_arquivo': planilha.tipo_arquivo.value,
            'dados': documentos
        }
        
        col_planilha.insert_one(documento)
        
        return {
            'message': 'Arquivo persistido com sucesso'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)