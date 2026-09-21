import filetype
from fastapi import UploadFile, HTTPException
from app.models.enums import EXTENSOES_PERMITIDAS
from app.utils.sem_magic_bytes import VALIDADORES_TEXTO
from pathlib import Path

TAMANHO_MAXIMO_MB = 10
TAMANHO_MAXIMO_BYTES = TAMANHO_MAXIMO_MB * 1024 * 1024

async def validar_tipo(arquivo: UploadFile) -> str:
    # todos os filetypes estão nos primeiros 261 bytes
    # não é necessário ler todo o arquivo para saber o tipo
    header = await arquivo.read(261)
    await arquivo.seek(0) # cursor volta para início do arquivo

    tipo = filetype.guess(header)
    if tipo is not None:
        if tipo.extension not in EXTENSOES_PERMITIDAS:
            raise HTTPException(400, 'Tipo de arquivo não permitido')
        return tipo.extension
    
    extensao = Path(arquivo.filename).suffix.lstrip('.').lower()
    validador = VALIDADORES_TEXTO.get(extensao)

    if validador is None:
        raise HTTPException(400, 'Tipo de arquivo não reconhecido')

    await validador(arquivo)
    return extensao

def validar_tamanho(arquivo: UploadFile) -> None:
    if not arquivo.size:
        raise HTTPException(400, 'Arquivo vazio')

    if arquivo.size > TAMANHO_MAXIMO_BYTES:
        raise HTTPException(413, f'Arquivo excede {TAMANHO_MAXIMO_MB}mb')

async def validar_anexo(arquivo: UploadFile) -> str: 
    validar_tamanho(arquivo)
    return await validar_tipo(arquivo)