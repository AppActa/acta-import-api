# ACTA Import API

API de importação de arquivos do **ACTA**. Responsável por receber, validar e persistir dados históricos no formato `.csv` e `.xlsx` no banco de dados MongoDB com o objetivo de contextualização de agentes de inteligência artificial para gerar contexto a fim de alimentar análises como o gráfico de Ishikawa.

---

## Funcionalidades

- Upload e validação de arquivos `.csv` e `.xlsx`
- Normalização automática dos nomes de colunas (`snake_case`, sem acentos)
- Suporte a múltiplas abas em arquivos `.xlsx`
- Limpeza automática de linhas e colunas vazias
- Persistência estruturada no MongoDB
- ID sequencial auto-incrementado

---

## Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Framework | FastAPI |
| Banco de dados | MongoDB via Pymongo|
| Leitura de arquivos | Pandas + openpyxl |
| Normalização | python-slugify |
| Variáveis de ambiente | python-dotenv |

---

## Estrutura do projeto

```
├── 📁 app
│   ├── 📁 database
│   │   └── 🐍 mongo.py
│   ├── 📁 models
│   │   └── 🐍 planilha.py
│   ├── 📁 routes
│   │   └── 🐍 uploads.py
│   ├── 📁 services
│   │   └── 🐍 import_service.py
│   └── 📁 utils
│       └── 🐍 utils.py
├── ⚙️ .gitignore
├── 📝 README.md
├── 🐍 main.py
└── 📄 requirements.txt
```

---

## Configuração

### Pré-requisitos

- Python 3.10 +
- MongoDB em execução

### Instalação

```bash
git clone https://github.com/AppActa/acta-import-api.git
cd acta-import-api
pip install -r requirements.txt
```

### Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=acta
```

### Execução

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8080`. A documentação pode ser acessada em `http://localhost:8080/docs`

---

## Endpoints

### `POST /csv/`

Importa um arquivo `.csv`

#### Form-data

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id_empresa` | `int` | ID da empresa |
| `id_ciclo` | `int` | ID do ciclo do PDCA |
| `arquivo` | `file` | Arquivo `.csv` |


### `POST /xlsx/`

Importa um arquivo `.xlsx`, suporte a múltiplas abas

#### Form-data

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id_empresa` | `int` | ID da empresa |
| `id_ciclo` | `int` | ID do ciclo do PDCA |
| `arquivo` | `file` | Arquivo `.xlsx` |

---

## Comportamento da importação

- Nomes de colunas são normalizadas para `snake_case` sem acentos ou carateres especiais
- Em arquivos `.xlsx`, cada aba é processada separadamente e identificada com o nome normalizado
- Linhas onde todas as colunas são nulas são removidas automaticamente
- Colunas sem nome (`unnamed_X`) e completamente vazias são descartadas
- Valores nulos são convertidos para null no documento MongoDB