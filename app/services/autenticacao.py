from os import getenv
from httpx import AsyncClient, RequestError
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import UsuarioAutenticado

ACTA_PG_API_URL = f'{getenv('ACTA_PG_API_URL')}/api/v1'
bearer = HTTPBearer()

async def obter_usuario_autenticado(credenciais: HTTPAuthorizationCredentials = Security(bearer)) -> UsuarioAutenticado:
    headers = {'Authorization': f'Bearer {credenciais.credentials}'}

    try:
        async with AsyncClient(timeout=60) as cliente:
            health = await cliente.get(f'{ACTA_PG_API_URL}/health')

            if health.is_error:
                raise HTTPException(503, 'acta-pg-api indisponível')
        
            resposta = await cliente.get(f'{ACTA_PG_API_URL}/me', headers=headers)
    except RequestError:
        raise HTTPException(503, 'Não foi possível consultar acta-pg-api')

    if resposta.status_code in (401, 403):
        raise HTTPException(401, 'Bearer token inválido')
        
    if resposta.is_error:
        raise HTTPException(502, 'Falha ao consultar usuário autenticado')

    try:
        return UsuarioAutenticado.model_validate(resposta.json())
    except (ValueError, TypeError):
        raise HTTPException(502, 'Resposta inválida de acta-pg-api')