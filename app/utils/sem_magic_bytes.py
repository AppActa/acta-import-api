from codecs import getincrementaldecoder
from csv import Sniffer, Error
from fastapi import UploadFile, HTTPException
from defusedxml.ElementTree import fromstring

async def _validar_text(arquivo: UploadFile) -> str:
    # lê apenas primeiros 4kb
    header = await arquivo.read(4096)
    await arquivo.seek(0)

    if b'\x00' in header:
        raise HTTPException(400, 'Arquivo não é um TXT puro')

    try:
        # se houver caractere incompleto no final do chunk não lança exceção
        # (pode ter sido fatiado ao pegar os primeiros 4kb)
        decoder = getincrementaldecoder('utf-8')()
        return decoder.decode(header, final=False)
    except UnicodeDecodeError:
        raise HTTPException(400, 'Arquivo TXT não está em UTF-8')

async def validar_plain(arquivo: UploadFile) -> None:
    await _validar_text(arquivo)
    

async def validar_csv(arquivo: UploadFile) -> None:
    amostra = await _validar_text(arquivo)

    try:
        Sniffer().sniff(amostra)
    except Error:
        raise HTTPException(400, 'Arquivo não é um CSV puro')

async def validar_svg(arquivo: UploadFile) -> None:
    conteudo = await arquivo.read()
    await arquivo.seek(0)

    try:
        root = fromstring(conteudo)
    except Exception:
        raise HTTPException(400, 'Arquivo não é um SVG puro')

    if not root.tag.endswith('svg'):
        raise HTTPException(400, 'Arquivo não é um SVG puro')

VALIDADORES_TEXTO ={
    'txt': validar_plain,
    'csv': validar_csv,
    'svg': validar_svg
}