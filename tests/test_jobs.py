from unittest.mock import Mock

from app.models.enums import Status
from app.schemas import UploadJob
from app.services import jobs

class Cursor:
    def __init__(self, retorno=(5, "Instituto J&F", 7)):
        self.executados = []
        self.retorno = retorno

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, parametros):
        self.executados.append((sql, parametros))

    def fetchone(self):
        return self.retorno

class Connection:
    def __init__(self):
        self.cursor_obj = Cursor()
        self.commits = 0

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.commits += 1

def test_processa_upload_com_sucesso(monkeypatch):
    conexao = Connection()
    job = UploadJob(id_anexo=42, id_usuario=3, conteudo=b"pdf", nome_original="arquivo.pdf", extensao="pdf")
    enviar_cloudinary = Mock(return_value={"url": "https://arquivo", "public_id": "42", "resource_type": "image"})
    monkeypatch.setattr(jobs, "conn_worker", lambda: _contexto(conexao))
    monkeypatch.setattr(jobs, "enviar_cloudinary", enviar_cloudinary)

    jobs.processar_upload(job)

    assert any(Status.ATIVO.value in parametros for _, parametros in conexao.cursor_obj.executados)
    assert enviar_cloudinary.call_args.kwargs == {
        "pasta": "acta-arquivos/instituto-j-f-f6ce836f/ciclo-7",
        "public_id": "42"
    }

class _contexto:
    def __init__(self, valor):
        self.valor = valor

    def __enter__(self):
        return self.valor

    def __exit__(self, *args):
        return False
