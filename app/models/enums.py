from enum import Enum

class TipoImagem(Enum):
    JPEG = 'image/jpeg'
    PNG = 'image/png'
    WEBP = 'image/webp'
    GIF = 'image/gif'
    SVG = 'image/svg+xml'
    BMP = 'image/bmp'
    TIFF = 'image/tiff'

class TipoArquivo(Enum):
    PDF = 'application/pdf'
    DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    PPTX = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    CSV = 'text/csv'
    TXT = 'text/plain'

class Categoria(Enum):
    TREINAMENTO = 'TREINAMENTO'
    PLANO_ACAO = 'PLANO_ACAO'
    CAUSA_RAIZ = 'CAUSA_RAIZ'
    PROBLEMA = 'PROBLEMA'
    META = 'META'
    RELATORIO = 'RELATORIO'
    LICAO_APRENDIDA = 'LICAO_APRENDIDA'
    FORMULARIO = 'FORMULARIO'
    EVIDENCIA = 'EVIDENCIA'
    OUTRO = 'OUTRO'

class Status(Enum):
    PROCESSANDO = 'PROCESSANDO'
    ATIVO = 'ATIVO'
    ERRO = 'ERRO'
    EXCLUIDO = 'EXCLUIDO'