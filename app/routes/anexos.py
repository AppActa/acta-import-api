from fastapi import APIRouter, Depends, File, UploadFile

from app.database.postgres import get_conn
from app.schemas import AnexoForm, UsuarioAutenticado
from app.services.anexos import consultar_anexo, processar_anexo
from app.services.autenticacao import obter_contexto_ia, obter_usuario_autenticado

router = APIRouter(prefix='/anexos', tags=['anexos'])

@router.post('', status_code=202)
async def post_anexo(arquivo: UploadFile = File(...), dados: AnexoForm = Depends(), conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return await processar_anexo(arquivo, dados, conn, usuario)

@router.post('/ia', status_code=202)
async def post_anexo_ia(arquivo: UploadFile = File(...), dados: AnexoForm = Depends(), conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_contexto_ia)):
    return await processar_anexo(arquivo, dados, conn, usuario)

@router.get('/ia/{id_anexo}')
def get_anexo_ia(id_anexo: int, conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_contexto_ia)):
    return consultar_anexo(conn, id_anexo, usuario.id_empresa)

@router.get('/{id_anexo}')
def get_anexo(id_anexo: int, conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return consultar_anexo(conn, id_anexo, usuario.id_empresa)
