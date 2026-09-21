from pydantic import BaseModel, Field
from datetime import datetime
from app.models.enums import TipoArquivo, Categoria, TipoImagem, Status

class AnexoRequest(BaseModel):
    id_empresa: int
    id_ciclo: int
    criado_por: int
    id_origem: int
    nome_arquivo: str
    tipo_arquivo: TipoArquivo | TipoImagem
    tamanho_arquivo: int
    bucket_arquivo: str
    caminho_arquivo: str | None = None
    categoria: Categoria
    descricao: str | None = None

class Anexo(AnexoRequest):
    id: int
    status: Status
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime | None = None
    excluido_em: datetime | None = None