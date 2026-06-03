from enum import Enum
from pydantic import BaseModel, Field

class TipoDocumento(Enum):
    XLSX = 'XLSX'
    CSV = 'CSV'
    PDF = 'PDF'
    PPTX = 'PPTX'

class Contexto(Enum):
    EVIDENCIA = 'Evidência'
    HISTORICO = 'Histórico'
    TREINAMENTO = 'Treinamento'
    PADRONIZACAO = 'Padronização'
    LICAO_APRENDIDA = 'Lição Aprendida'

class Documento(BaseModel):
    id_empresa:               int = Field(..., description='ID da empresa no sistema ACTA', example=1)
    id_ciclo:                 int = Field(..., description='ID do ciclo de PDCA destino no sistema ACTA', example=6)
    tipo_documento: TipoDocumento = Field(..., description='Enum de tipo de documento', example='XLSX')
    contexto:            Contexto = Field(..., description='Enum de contexto do upload do documento', example='Evidência')
    nome_documento:           str = Field(..., description='Nome original do documento', example='evidencia.pdf')