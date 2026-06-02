from enum import Enum
from pydantic import BaseModel, Field

class TipoArquivo(Enum):
    XLSX = 'XLSX'
    CSV = 'CSV'

class Planilha(BaseModel):
    id_empresa:           int = Field(..., description='ID da empresa no sistema ACTA', example=1)
    id_ciclo:             int = Field(..., description='ID do ciclo de PDCA destino no sistema ACTA', example=6)
    tipo_arquivo: TipoArquivo = Field(..., description='Enum de tipo de arquivo', example='XLSX')