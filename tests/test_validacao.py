from io import BytesIO
import asyncio

import pytest
from fastapi import HTTPException, UploadFile

from app.utils.validacao import validar_anexo


def arquivo(nome: str, conteudo: bytes, tamanho: int | None = None) -> UploadFile:
    upload = UploadFile(filename=nome, file=BytesIO(conteudo))
    upload.size = len(conteudo) if tamanho is None else tamanho
    return upload


def test_aceita_txt_utf8():
    upload = arquivo("evidencia.txt", "conteúdo válido".encode())

    assert asyncio.run(validar_anexo(upload)) == "txt"


def test_rejeita_arquivo_vazio():
    with pytest.raises(HTTPException) as erro:
        asyncio.run(validar_anexo(arquivo("vazio.txt", b"")))

    assert erro.value.status_code == 400
    assert erro.value.detail == "Arquivo vazio"


def test_rejeita_arquivo_maior_que_o_limite():
    upload = arquivo("grande.txt", b"conteudo", tamanho=10 * 1024 * 1024 + 1)

    with pytest.raises(HTTPException) as erro:
        asyncio.run(validar_anexo(upload))

    assert erro.value.status_code == 413


def test_rejeita_txt_com_byte_nulo():
    with pytest.raises(HTTPException) as erro:
        asyncio.run(validar_anexo(arquivo("invalido.txt", b"texto\x00invalido")))

    assert erro.value.status_code == 400
    assert erro.value.detail == "Arquivo não é um TXT puro"


def test_rejeita_extensao_nao_reconhecida():
    with pytest.raises(HTTPException) as erro:
        asyncio.run(validar_anexo(arquivo("arquivo.exe", b"conteudo")))

    assert erro.value.status_code == 400
    assert erro.value.detail == "Tipo de arquivo não reconhecido"
