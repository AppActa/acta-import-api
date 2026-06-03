from fastapi import APIRouter, UploadFile, File, Form
from app.services.import_service import upload_csv, upload_xlsx
from app.models.documento import Documento, TipoDocumento, Contexto

router = APIRouter()

@router.post(
        '/csv/',
        summary='Upload de CSV',
        response_description='Confirmação de persistência',
        responses = {
            200: {'description': 'Documento salvo com sucesso'},
            400: {'description': 'Documento iválido ou vazio'},
            500: {'description': 'Erro interno no servidor'}
        }
    )
async def post_csv(
    id_empresa: int = Form(..., description='ID da empresa no sistema ACTA', examples=[1]),
    id_ciclo: int = Form(..., description='ID do ciclo de PDCA destino no sistema ACTA', examples=[6]),
    contexto: Contexto = Form(..., description='Contexto da requisição', examples=['Evidência']),
    arquivo: UploadFile = File(..., description='Documento .CSV')
):
    """
    Importa um arquivo .csv vinculado a um ciclo PDCA.
    
    - Valida a extensão do arquivo
    - Normaliza nomes das colunas para snake_case
    - Persiste dados no MongoDB associados a empresa e ao ciclo
    """
    
    documento = Documento(
        id_empresa = id_empresa,
        id_ciclo = id_ciclo,
        tipo_documento = TipoDocumento.CSV,
        contexto = contexto,
        nome_documento = arquivo.filename
    )
    
    return await upload_csv(arquivo, documento)

@router.post(
        '/xlsx/',
        summary='Upload de XLSX',
        response_description='Confirmação de persistência',
        responses = {
            200: {'description': 'Documento salvo com sucesso'},
            400: {'description': 'Documento iválido ou vazio'},
            500: {'description': 'Erro interno no servidor'}
        }
    )
async def post_xlsx(
    id_empresa: int = Form(..., description='ID da empresa no sistema ACTA', examples=[1]),
    id_ciclo: int = Form(..., description='ID do ciclo de PDCA destino no sistema ACTA', examples=[6]),
    contexto: Contexto = Form(..., description='Contexto da requisição', examples=['Evidência']),
    arquivo: UploadFile = File(..., description='Documento .XLSX')
):
    """
    Importa um arquivo .xlsx vinculado a um ciclo PDCA.
    
    - Valida a extensão do arquivo
    - Normaliza nomes das colunas para snake_case
    - Captura dados de todas as planilhas do arquivo
    - Persiste dados no MongoDB associados a empresa e ao ciclo
    """
    
    documento = Documento(
        id_empresa = id_empresa,
        id_ciclo = id_ciclo,
        tipo_documento = TipoDocumento.XLSX,
        contexto = contexto,
        nome_documento = arquivo.filename
    )
    
    return await upload_xlsx(arquivo, documento)