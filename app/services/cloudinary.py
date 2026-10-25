import re
import unicodedata

from cloudinary import config as cloudinary_config
from cloudinary.api import subfolders
from cloudinary.exceptions import Error, NotFound
from cloudinary.uploader import upload
from fastapi import HTTPException
from app.config import CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME

cloudinary_config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

# reforçar tipo raw, cloudinary não sabe lidar com esses arquivos
EXTENSOES_RAW = {'docx', 'pptx', 'xlsx', 'csv', 'txt'}

def normalizar_nome_empresa(nome: str) -> str:
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', nome).strip('-')

def listar_subpastas(pasta: str):
    proxima_pagina = None
    while True:
        try:
            resultado = subfolders(pasta, max_results=500, next_cursor=proxima_pagina)
        except NotFound:
            return
        except Error:
            raise HTTPException(503, 'Não foi possível consultar as pastas no Cloudinary')

        for subpasta in resultado['folders']:
            yield subpasta['name']

        proxima_pagina = resultado.get('next_cursor')
        if not proxima_pagina:
            return

# erros serão propagados para a fila no redis
def enviar_cloudinary(caminho_arquivo: str, nome_original: str, extensao: str, pasta: str = 'anexos', public_id: str | None = None) -> dict:
    resultado = upload(
        caminho_arquivo,
        folder=pasta,
        public_id=public_id,
        resource_type='raw' if extensao in EXTENSOES_RAW else 'auto',
        filename=nome_original,
        use_filename=True,
        unique_filename=True
    )
    
    return {
        'url': resultado['secure_url'],
        'public_id': resultado['public_id'],
        'resource_type': resultado['resource_type']
    }