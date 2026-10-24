from httpx import AsyncClient, RequestError
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import ACTA_AUTH_API_URL
from app.schemas import UsuarioAutenticado
bearer = HTTPBearer()

async def obter_usuario_autenticado(credenciais: HTTPAuthorizationCredentials = Security(bearer)) -> UsuarioAutenticado:
    headers = {'Authorization': f'Bearer {credenciais.credentials}'}

    try:
        async with AsyncClient(timeout=60) as cliente:
            resposta = await cliente.get(f'{ACTA_AUTH_API_URL.rstrip("/")}/contexto', headers=headers)
    except RequestError:
        raise HTTPException(503, 'Não foi possível consultar acta-auth-api')

    if resposta.status_code == 401:
        raise HTTPException(401, 'Bearer token inválido')

    if resposta.status_code == 403:
        raise HTTPException(403, 'Usuário não autorizado')

    if resposta.status_code == 503:
        raise HTTPException(503, 'acta-auth-api indisponível')
        
    if resposta.is_error:
        raise HTTPException(502, 'Falha ao consultar usuário autenticado')

    try:
        dados_usuario = resposta.json()
        if not isinstance(dados_usuario, dict):
            raise ValueError
    except (ValueError, TypeError):
        raise HTTPException(502, 'Resposta inválida de acta-auth-api')

    try:
        return UsuarioAutenticado.model_validate(dados_usuario)
    except (ValueError, TypeError):
        raise HTTPException(502, 'Resposta inválida de acta-auth-api')