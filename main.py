from fastapi import FastAPI
from app.routes.anexos import router as anexos_router

app = FastAPI(
    title='ACTA Import API',
    description='API de importação de arquivos de .pdf, .docx, .pptx, .txt, .xlsx, .csv e imagens para ciclos PDCA do ACTA'
)

app.include_router(anexos_router)