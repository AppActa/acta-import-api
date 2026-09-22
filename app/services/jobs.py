from rq import get_current_job
from pathlib import Path
from app.database.postgres import conn_worker
from app.services.cloudinary import enviar_cloudinary
from app.models.enums import Status
from app.schemas import UploadJob

def processar_upload(job: UploadJob) -> None:
    with conn_worker() as conn:
        try:
            _atualizar_status(conn, job.id_anexo, Status.PROCESSANDO)
            resultado = enviar_cloudinary(
                job.caminho_arquivo,
                job.nome_original,
                job.extensao,
                public_id=f'anexos/{job.id_anexo}',
            )

            _atualizar_sucesso(conn, job.id_anexo, resultado)
            _limpar_temp(job.caminho_arquivo) # só remove quando dá certo
        except Exception:
            job = get_current_job()
            ultima_tentativa = job is None or not job.retries_left

            # se não for a útlima tentativa deixa o arquivo e status processando
            # redis chama a função de novo...
            if ultima_tentativa:
                _atualizar_status(conn, job.id_anexo, Status.ERRO)
                _limpar_temp(job.caminho_arquivo)
            raise

def _atualizar_status(conn, id_anexo: int, status: Status) -> None:
    with conn.cursor() as cursor:
        cursor.execute('UPDATE pdca.anexo SET status = %s WHERE id = %s', (status.value, id_anexo))
    conn.commit()

def _atualizar_sucesso(conn, id_anexo: int, resultado: dict) -> None:
    with conn.cursor() as cursor:
        cursor.execute('UPDATE pdca.anexo SET status = %s, caminho_arquivo = %s WHERE id = %s', (Status.ATIVO.value, resultado['url'], id_anexo))
    conn.commit()

def _limpar_temp(caminho_arquivo: str) -> None:
    Path(caminho_arquivo).unlink(missing_ok=True)