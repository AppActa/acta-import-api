from pymongo import MongoClient, ReturnDocument
from fastapi import HTTPException
from app.models.documento import Documento
from dotenv import load_dotenv
from os import getenv

# capturando informações do .env
load_dotenv()

# configurações de conexão com Mongo
MONGO_URL          = getenv('MONGO_URL')
DB_NAME            = getenv('DB_NAME')
COLLECTION_NAME    = 'documentos'
COLLECTION_COUNTER = 'counter'

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
col_documento = db[COLLECTION_NAME]
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

# função para inserir documento no banco
def inserir_documento(documento: Documento, dados) -> dict:
    try:
        if not dados:
            raise HTTPException(status_code=400, detail='Documento vazio ou corrompido')
        
        # inserindo no banco        
        col_documento.insert_one({
            '_id': get_next_id(),
            'id_empresa': documento.id_empresa,
            'id_ciclo': documento.id_ciclo,
            'nome_documento': documento.nome_documento,
            'tipo_documento': documento.tipo_documento.value,
            'contexto': documento.contexto.value,
            'dados': dados
        })
        
        return {
            'status': 201,
            'message': 'Documento persistido com sucesso'
        }
    except:
        raise HTTPException(status_code=500, detail='Erro no banco de dados')