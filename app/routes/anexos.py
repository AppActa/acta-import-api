from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from rq import Retry
from app.database.postgres import get_conn
from app.utils.validacao import validar_anexo
from app.services.fila import fila_uploads
from app.services.jobs import processar_upload
from app.models.enums import Status
from app.schemas import AnexoForm, UploadJob, UsuarioAutenticado
from app.services.autenticacao import obter_contexto_ia, obter_usuario_autenticado

DIR_TEMP = Path('/tmp/uploads')
DIR_TEMP.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix='/anexos', tags=['anexos'])

@router.post('', status_code=202)
async def post_anexo(arquivo: UploadFile = File(...), dados: AnexoForm = Depends(), conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return await _processar_anexo(arquivo, dados, conn, usuario)

@router.post('/ia', status_code=202)
async def post_anexo_ia(arquivo: UploadFile = File(...), dados: AnexoForm = Depends(), conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_contexto_ia)):
    return await _processar_anexo(arquivo, dados, conn, usuario)

@router.get('/ia/{id_anexo}')
def get_anexo_ia(id_anexo: int, conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_contexto_ia)):
    return _get_anexo(conn, id_anexo, usuario.id_empresa)

@router.get('/{id_anexo}')
def get_anexo(id_anexo: int, conn=Depends(get_conn), usuario: UsuarioAutenticado = Depends(obter_usuario_autenticado)):
    return _get_anexo(conn, id_anexo, usuario.id_empresa)

async def _processar_anexo(arquivo: UploadFile, dados: AnexoForm, conn, usuario: UsuarioAutenticado):
    _validar_ciclo_empresa(conn, dados.id_ciclo, usuario.id_empresa)
    extensao = await validar_anexo(arquivo)

    id_anexo = _inserir_metadados(conn, arquivo, dados, extensao, usuario)
    caminho_temp = DIR_TEMP / f'{id_anexo}_{uuid4().hex}{Path(arquivo.filename).suffix}'

    try:
        caminho_temp.write_bytes(await arquivo.read())
    except Exception:
        _atualizar_status_erro(conn, id_anexo, usuario.id_usuario)
        raise HTTPException(500, 'Falha ao salvar arquivo temporário')

    try:
        fila_uploads.enqueue(
            processar_upload, UploadJob(
            id_anexo=id_anexo,
            id_usuario=usuario.id_usuario,
            conteudo=caminho_temp.read_bytes(),
            nome_original=arquivo.filename,
            extensao=extensao),
            retry=Retry(max=3, interval=[10, 30, 60]), result_ttl=3600, failure_ttl=86400
        )
    except Exception:
        _atualizar_status_erro(conn, id_anexo, usuario.id_usuario)
        caminho_temp.unlink(missing_ok=True)
        raise HTTPException(503, 'Não foi possível enfileirar o processamento')

    caminho_temp.unlink(missing_ok=True)
    return {'id': id_anexo, 'status': Status.PROCESSANDO.value}

def _get_anexo(conn, id_anexo: int, id_empresa: int) -> dict:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, status, caminho_arquivo
            FROM pdca.anexo
            WHERE id = %s AND id_empresa = %s AND excluido_em IS NULL
            """,
            (id_anexo, id_empresa),
        )
        anexo = cursor.fetchone()

    if anexo is None:
        raise HTTPException(404, 'Anexo não encontrado')

    return {
        'id': anexo[0],
        'status': anexo[1],
        'enviado': anexo[1] == Status.ATIVO.value and bool(anexo[2]),
        'url': anexo[2],
    }

def _validar_ciclo_empresa(conn, id_ciclo: int, id_empresa: int) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            'SELECT 1 FROM pdca.ciclo WHERE id = %s AND id_empresa = %s',
            (id_ciclo, id_empresa),
        )
        if cursor.fetchone() is None:
            raise HTTPException(403, 'Ciclo não pertence à empresa do usuário')

def _inserir_metadados(conn, arquivo: UploadFile, dados: AnexoForm, extensao: str, usuario: UsuarioAutenticado) -> int:
    with conn.cursor() as cursor:
        cursor.execute("SELECT set_config('app.current_user_id', %s, true)", (str(usuario.id_usuario),))
        cursor.execute("""
        INSERT INTO pdca.anexo (id_empresa, id_ciclo, criado_por, id_origem, nome_arquivo, tipo_arquivo, tamanho_arquivo, bucket_arquivo, caminho_arquivo, categoria, descricao, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, %s)
        RETURNING id
        """, 
        (usuario.id_empresa, dados.id_ciclo, usuario.id_usuario, dados.id_origem, arquivo.filename, arquivo.content_type or extensao, arquivo.size, 'cloudinary', dados.categoria.value, dados.descricao, Status.PROCESSANDO.value))

        id_anexo = cursor.fetchone()[0]
    conn.commit()
    return id_anexo

def _atualizar_status_erro(conn, id_anexo: int, id_usuario: int) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT set_config('app.current_user_id', %s, true)",
            (str(id_usuario),),
        )
        cursor.execute('UPDATE pdca.anexo SET status = %s WHERE id = %s', (Status.ERRO.value, id_anexo))
    conn.commit()