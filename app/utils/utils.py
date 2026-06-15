from slugify import slugify
from re import sub

def normalizar_nomes(nome_coluna):
    nome_coluna = str(nome_coluna)
    nome_coluna = sub(r'([a-z0-9])([A-Z])', r'\1_\2', nome_coluna)
    return slugify(nome_coluna, separator='_')