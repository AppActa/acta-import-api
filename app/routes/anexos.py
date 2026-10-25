from fastapi import APIRouter, Depends, File, UploadFile

from app.database.postgres import get_conn
from app.schemas import AnexoForm, PastaEmpresaResponse, UsuarioAutenticado
from app.services.anexos import consultar_anexo, processar_anexo
from app.services.autenticacao import obter_usuario_autenticado
from app.services.pastas import consultar_pasta_empresa

router = APIRouter(prefix='/anexos', tags=['anexos'])

@router.post('', status_code=202)
async def post_anexo(arquivo: UploadFile = File(...), dados: AnexoForm = Depends(), conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return await processar_anexo(arquivo, dados, conn, usuario)

@router.post('/ia', status_code=202)
async def post_anexo_ia(arquivo: UploadFile = File(...), dados: AnexoForm = Depends(), conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return await processar_anexo(arquivo, dados, conn, usuario)

@router.get('/pasta-empresa', response_model=PastaEmpresaResponse, summary='Consultar pasta da empresa no Cloudinary')
def get_pasta_empresa(conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return consultar_pasta_empresa(conn, usuario.id_empresa)

@router.get('/ia/{id_anexo}')
def get_anexo_ia(id_anexo: int, conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return consultar_anexo(conn, id_anexo, usuario.id_empresa)

@router.get('/{id_anexo}')
def get_anexo(id_anexo: int, conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return consultar_anexo(conn, id_anexo, usuario.id_empresa)