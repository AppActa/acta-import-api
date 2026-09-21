from fastapi import Form
from pydantic import BaseModel
from app.models.enums import Categoria

class AnexoForm(BaseModel):
    def __init__(
        self,
        id_empresa: int = Form(...),
        id_ciclo: int = Form(...),
        criado_por: int = Form(...),
        id_origem: int = Form(...),
        categoria: Categoria = Form(...),
        descricao: str | None = Form(None),
    ):
        self.id_empresa = id_empresa
        self.id_ciclo = id_ciclo
        self.criado_por = criado_por
        self.id_origem = id_origem
        self.categoria = categoria
        self.descricao = descricao


class UploadJob(BaseModel):
    id_anexo: int
    caminho_arquivo: str
    nome_original: str
    extensao: str