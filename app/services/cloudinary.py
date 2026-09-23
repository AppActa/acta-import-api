from cloudinary import config
from cloudinary.uploader import upload
from os import getenv
from dotenv import load_dotenv

load_dotenv()

CLOUD_NAME = getenv('CLOUDINARY_CLOUD_NAME')
API_KEY = getenv('CLOUDINARY_API_KEY')
API_SECRET = getenv('CLOUDINARY_API_SECRET')

config(cloud_name=CLOUD_NAME, api_key=API_KEY, api_secret=API_SECRET, secure=True)

# reforçar tipo raw, cloudinary não sabe lidar com esses arquivos
EXTENSOES_RAW = {'docx', 'pptx', 'xlsx', 'csv', 'txt'}

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