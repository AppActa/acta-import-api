from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routes.anexos import router as anexos_router

app = FastAPI(
    title='ACTA Import API',
    description='API de importação de arquivos de .pdf, .docx, .pptx, .txt, .xlsx, .csv e imagens para ciclos PDCA do ACTA'
)

def _resposta_erro(status_code: int, mensagens: list[str]) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            'mensagens': mensagens,
            'httpStatus': status_code,
            'timestamp': datetime.now().isoformat(timespec='seconds'),
        },
    )

@app.exception_handler(HTTPException)
async def tratar_http_exception(_request: Request, exc: HTTPException):
    detalhe = exc.detail if isinstance(exc.detail, list) else [str(exc.detail)]
    return _resposta_erro(exc.status_code, [str(mensagem) for mensagem in detalhe])

@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(_request: Request, exc: RequestValidationError):
    mensagens = []
    for erro in exc.errors():
        campo = '.'.join(str(parte) for parte in erro['loc'] if parte != 'body')
        mensagens.append(f"{campo}: {erro['msg']}" if campo else erro['msg'])
    return _resposta_erro(422, mensagens)

@app.exception_handler(Exception)
async def tratar_erro_interno(_request: Request, exc: Exception):
    return _resposta_erro(500, ['Erro interno do servidor'])

app.include_router(anexos_router)