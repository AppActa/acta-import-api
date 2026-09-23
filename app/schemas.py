from fastapi import Form
from pydantic import BaseModel, Field
from app.models.enums import Categoria

class AnexoForm:
    def __init__(
        self,
        id_ciclo: int = Form(...),
        id_origem: int = Form(...),
        categoria: Categoria = Form(...),
        descricao: str | None = Form(None),
    ):
        self.id_ciclo = id_ciclo
        self.id_origem = id_origem
        self.categoria = categoria
        self.descricao = descricao

class UploadJob(BaseModel):
    id_anexo: int
    id_usuario: int
    conteudo: bytes
    nome_original: str
    extensao: str

class UsuarioAutenticado(BaseModel):
    id_usuario: int = Field(alias='idUsuario')
    id_empresa: int = Field(alias='idEmpresa')