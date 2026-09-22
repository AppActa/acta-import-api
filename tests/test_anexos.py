from io import BytesIO
import asyncio
from pathlib import Path
from unittest.mock import ANY, AsyncMock, Mock
import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers
from app.models.enums import Categoria, Status
from app.routes import anexos
from app.schemas import AnexoForm, UsuarioAutenticado

class Cursor:
    def __init__(self, retorno=(42,)):
        self.retorno = retorno
        self.executados = []

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

def dados():
    return AnexoForm(7, 9, Categoria.EVIDENCIA, "descrição")

def usuario():
    return UsuarioAutenticado(idUsuario=3, idEmpresa=5)

def test_insere_metadados_com_usuario_autenticado():
    conn = Connection()
    arquivo = UploadFile(filename="arquivo.pdf", file=BytesIO(b"pdf"), headers=Headers({"content-type": "application/pdf"}))
    arquivo.size = 3

    resultado = anexos._inserir_metadados(conn, arquivo, dados(), "pdf", usuario())

    assert resultado == 42
    assert conn.commits == 1
    assert "INSERT INTO pdca.anexo" in conn.cursor_obj.executados[1][0]
    assert conn.cursor_obj.executados[1][1][:4] == (5, 7, 3, 9)

def test_criar_anexo_enfileira_upload_e_retorna_aceito(monkeypatch):
    tmp_path = Path("tests/.tmp_uploads")
    tmp_path.mkdir(exist_ok=True)
    monkeypatch.setattr(anexos, "DIR_TEMP", tmp_path)
    monkeypatch.setattr(anexos, "validar_anexo", AsyncMock(return_value="pdf"))
    monkeypatch.setattr(anexos, "_inserir_metadados", Mock(return_value=42))
    enqueue = Mock()
    monkeypatch.setattr(anexos.fila_uploads, "enqueue", enqueue)

    arquivo = UploadFile(filename="arquivo.pdf", file=BytesIO(b"pdf"))
    arquivo.size = 3
    resposta = asyncio.run(anexos.criar_anexo(arquivo, dados(), Connection(), usuario()))

    assert resposta == {"id": 42, "status": Status.PROCESSANDO.value}
    enqueue.assert_called_once()
    assert enqueue.call_args.args[1].id_anexo == 42
    assert enqueue.call_args.args[1].extensao == "pdf"

def test_criar_anexo_marca_erro_se_falhar_ao_enfileirar(monkeypatch):
    tmp_path = Path("tests/.tmp_uploads")
    tmp_path.mkdir(exist_ok=True)
    monkeypatch.setattr(anexos, "DIR_TEMP", tmp_path)
    monkeypatch.setattr(anexos, "validar_anexo", AsyncMock(return_value="pdf"))
    monkeypatch.setattr(anexos, "_inserir_metadados", Mock(return_value=42))
    monkeypatch.setattr(anexos.fila_uploads, "enqueue", Mock(side_effect=RuntimeError))
    atualizar = Mock()
    monkeypatch.setattr(anexos, "_atualizar_status_erro", atualizar)

    with pytest.raises(Exception) as erro:
        asyncio.run(anexos.criar_anexo(
            UploadFile(filename="arquivo.pdf", file=BytesIO(b"pdf")),
            dados(),
            Connection(),
            usuario(),
        ))

    assert erro.value.status_code == 503
    atualizar.assert_called_once_with(ANY, 42, 3)