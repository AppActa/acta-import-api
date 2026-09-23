from pathlib import Path
from tempfile import NamedTemporaryFile
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

            resultado = enviar_cloudinary(caminho_temp, job.nome_original, job.extensao, public_id=f'anexos/{job.id_anexo}')

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