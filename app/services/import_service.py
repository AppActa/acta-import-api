from fastapi import UploadFile, HTTPException
from app.database.mongo import inserir_documento
from app.models.documento import Documento, TipoDocumento
from app.utils.utils import normalizar_nomes
import pandas as pd
from io import BytesIO
from re import match

async def _verificador(arquivo: UploadFile, extensao: TipoDocumento):
    # verificar se extensão de arquivo é suportada
    if not arquivo.filename.upper().endswith(extensao.value.upper()):
        raise HTTPException(status_code=400, detail=f'Apenas arquivos .{extensao.value.upper()} são permitidos')
    
    # variáveis de leitura de arquivo
    conteudo = await arquivo.read()
    return BytesIO(conteudo) # retorna buffer para ser convertido

async def upload_csv(arquivo: UploadFile, documento: Documento):
    buffer = await _verificador(arquivo, documento.tipo_documento)
    df = pd.read_csv(buffer, engine='c')
    
    df.columns = [normalizar_nomes(c) for c in df.columns]
    dados = df.to_dict(orient='records')
    
    return inserir_documento(documento, dados)

async def upload_xlsx(arquivo: UploadFile, documento: Documento):
    buffer = await _verificador(arquivo, documento.tipo_documento)
    df = pd.read_excel(buffer, sheet_name=None, engine='openpyxl')    
    dados_por_planilha = {}
    
    # itera cada uma das documentos
    for planilha, dados in df.items():
        dados['planilha'] = normalizar_nomes(planilha)        
        dados.columns = [normalizar_nomes(c) for c in dados.columns]
        
        dados = dados.astype(object).where(pd.notna(dados), None) # converte todas as colunas para object, e valores nulos para None
        dados = dados.dropna(how='all') # exclui linhas onde todas as colunas são nulas
        dados = dados.drop(columns=[c for c in dados.columns if match(r'^unnamed_\d+$', c) and dados[c].isna().all()])
        
        # insere dados da planilha no dicionário
        dados_por_planilha[planilha] = dados.to_dict(orient='records')

    return inserir_documento(documento, dados_por_planilha)