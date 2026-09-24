import re
import unicodedata
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import NAMESPACE_URL, uuid5
from rq import get_current_job
from app.database.postgres import conn_worker
from app.models.enums import Status
from app.schemas import UploadJob
from app.services.cloudinary import enviar_cloudinary

def processar_upload(job: UploadJob) -> None:
    caminho_temp = None
    with conn_worker() as conn:
        try:
            _configurar_usuario(conn, job.id_usuario)

            with NamedTemporaryFile(suffix=f'.{job.extensao}', delete=False) as arquivo_temp:
                arquivo_temp.write(job.conteudo)
                caminho_temp = arquivo_temp.name
            _atualizar_status(conn, job.id_anexo, job.id_usuario, Status.PROCESSANDO)

            pasta = _obter_pasta_cloudinary(conn, job.id_anexo)
            resultado = enviar_cloudinary(
                caminho_temp,
                job.nome_original,
                job.extensao,
                pasta=pasta,
                public_id=str(job.id_anexo)
            )

            _atualizar_sucesso(conn, job.id_anexo, job.id_usuario, resultado)
        except Exception:
            rq_job = get_current_job()
            ultima_tentativa = rq_job is None or not rq_job.retries_left
            
            if ultima_tentativa:
                _atualizar_status(conn, job.id_anexo, job.id_usuario, Status.ERRO)
            raise
        finally:
            if caminho_temp:
                _limpar_temp(caminho_temp)

def _configurar_usuario(conn, id_usuario: int) -> None:
    with conn.cursor() as cursor:
        cursor.execute("SELECT set_config('app.current_user_id', %s, true)", (str(id_usuario),),)

def _obter_pasta_cloudinary(conn, id_anexo: int) -> str:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT e.id, e.nome, a.id_ciclo
            FROM pdca.anexo a
            JOIN public.empresa e ON e.id = a.id_empresa
            WHERE a.id = %s
            """,
            (id_anexo,)
        )
        empresa = cursor.fetchone()

    if empresa is None:
        raise ValueError('Empresa do anexo não encontrada')

    id_empresa, nome_empresa, id_ciclo = empresa
    nome_normalizado = unicodedata.normalize('NFKD', nome_empresa).encode('ascii', 'ignore').decode().lower()
    nome_normalizado = re.sub(r'[^a-z0-9]+', '-', nome_normalizado).strip('-')
    uuid_curto = uuid5(NAMESPACE_URL, f'acta:empresa:{id_empresa}').hex[:8]

    return f'acta-arquivos/{nome_normalizado}-{uuid_curto}/ciclo-{id_ciclo}'

def _atualizar_status(conn, id_anexo: int, id_usuario: int, status: Status) -> None:
    _configurar_usuario(conn, id_usuario)
    with conn.cursor() as cursor:
        cursor.execute('UPDATE pdca.anexo SET status = %s WHERE id = %s', (status.value, id_anexo))
    conn.commit()

def _atualizar_sucesso(conn, id_anexo: int, id_usuario: int, resultado: dict) -> None:
    _configurar_usuario(conn, id_usuario)
    with conn.cursor() as cursor:
        cursor.execute('UPDATE pdca.anexo SET status = %s, caminho_arquivo = %s WHERE id = %s', (Status.ATIVO.value, resultado['url'], id_anexo))
    conn.commit()

def _limpar_temp(caminho_arquivo: str) -> None:
    Path(caminho_arquivo).unlink(missing_ok=True)