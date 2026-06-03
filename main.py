from fastapi import FastAPI
from app.routes.uploads import router

app = FastAPI(
    title = 'ACTA Import API',
    description = 'API de importação de arquivos CSV e XLSX para ciclos PDCA do ACTA',
    version = '1.2.0'
)

app.include_router(router, prefix='/uploads', tags=['Uploads'])