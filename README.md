# 📎 ACTA Import API

API responsável pelo recebimento e processamento assíncrono de anexos utilizados nos ciclos PDCA do ACTA.

O serviço valida o arquivo recebido, registra seus metadados no PostgreSQL, salva uma cópia temporária e envia um job para processamento no Redis. O worker realiza o upload para o Cloudinary e atualiza o status do anexo no banco.

## 📌 Visão geral

O `acta-import-api` atua como um serviço especializado do ecossistema ACTA:

1. recebe o arquivo e os dados do anexo;
2. consulta o usuário autenticado no `acta-pg-api`;
3. valida tamanho, extensão e conteúdo;
4. registra os metadados em `pdca.anexo`;
5. enfileira o processamento no Redis;
6. envia o arquivo ao Cloudinary pelo worker;
7. atualiza o status e o caminho do arquivo no PostgreSQL.

O processamento do upload é assíncrono. Portanto, uma resposta `202 Accepted` confirma o recebimento e o enfileiramento, mas não confirma que o upload no Cloudinary já terminou.

## 🧰 Redis e fila de processamento

O Redis funciona como intermediário entre a API e o worker. A API não envia o arquivo diretamente ao Cloudinary durante a requisição; depois de salvar o arquivo temporário e os metadados, publica um `UploadJob` na fila `uploads`.

O worker executa continuamente essa fila, recupera o job, envia o arquivo ao Cloudinary e atualiza o registro no PostgreSQL. Assim, o processamento pesado acontece fora da requisição HTTP e o endpoint pode responder rapidamente com `202 Accepted`.

O Redis armazena a fila e o estado necessário para o RQ controlar a execução. Se o processamento falhar, o job possui até três tentativas, com intervalos de 10, 30 e 60 segundos. O arquivo temporário é mantido durante as tentativas e removido quando o processamento termina com sucesso ou falha definitiva.

O Redis precisa estar acessível tanto pela API, que enfileira os jobs, quanto pelo worker, que os consome. Em ambientes com autenticação, configure também `REDIS_PASSWORD` no ambiente da aplicação e do worker.

## ✨ Funcionalidades

- Upload de arquivos para anexos de ciclos PDCA.
- Validação de arquivos PDF, DOCX, PPTX, XLSX e imagens.
- Validação específica para TXT, CSV e SVG.
- Limite de 10 MB por arquivo.
- Autenticação por Bearer Token delegada ao `acta-pg-api`.
- Registro do usuário e da empresa a partir do contexto autenticado.
- Processamento assíncrono com Redis Queue (RQ).
- Upload de arquivos para o Cloudinary.
- Atualização dos status `PROCESSANDO`, `ATIVO` e `ERRO`.



## 🛠️ Tecnologias


| Tecnologia   | Uso                                  |
| ------------ | ------------------------------------ |
| Python       | Linguagem da aplicação               |
| FastAPI      | API HTTP                             |
| PostgreSQL   | Metadados dos anexos                 |
| Redis        | Fila de processamento                |
| RQ           | Execução dos jobs assíncronos        |
| Cloudinary   | Armazenamento dos arquivos           |
| `filetype`   | Identificação do tipo por assinatura |
| `defusedxml` | Validação segura de SVG              |
| Pytest       | Testes unitários                     |




## ✅ Pré-requisitos

- Python 3.11 ou superior.
- PostgreSQL acessível com a tabela `pdca.anexo` já criada.
- Redis acessível para a fila `uploads`.
- Conta e credenciais do Cloudinary.
- `acta-pg-api` acessível para autenticação e consulta do usuário.

As dependências Python usadas pela aplicação devem estar instaladas no ambiente virtual do projeto.

## ⚙️ Configuração

Crie um arquivo `.env` local a partir de `.env.example`:

```env
DB_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco

CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret

ACTA_PG_API_URL=https://acta-pg-api.onrender.com/api/v1
ACTA_IA_TOKEN=defina-um-token-interno

REDIS_HOST=localhost
REDIS_PORT=6379
```

Nunca versione senhas, tokens ou credenciais do Cloudinary. O arquivo `.env.example` deve conter somente valores de referência.

## 🚀 Execução local

Inicie a API:

```bash
uvicorn main:app --reload
```

Por padrão, o servidor fica disponível em `http://localhost:8000`.

Em outro terminal, inicie o worker da fila:

```bash
python worker.py
```

A API e o worker precisam estar em execução para que o ciclo completo de importação seja processado.

## 📚 Documentação

Com a API em execução:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI: `http://localhost:8000/openapi.json`



## 🔌 Endpoint principal



### Criar anexo

```http
POST /anexos
Authorization: Bearer <TOKEN>
Content-Type: multipart/form-data
```

Campos do formulário:


| Campo       | Tipo    | Obrigatório | Descrição                        |
| ----------- | ------- | ----------- | -------------------------------- |
| `arquivo`   | arquivo | Sim         | Arquivo que será importado       |
| `id_ciclo`  | inteiro | Sim         | Identificador do ciclo PDCA      |
| `id_origem` | inteiro | Sim         | Identificador da origem do anexo |
| `categoria` | enum    | Sim         | Categoria do anexo               |
| `descricao` | texto   | Não         | Descrição do arquivo             |


Categorias disponíveis:

`TREINAMENTO`, `PLANO_ACAO`, `CAUSA_RAIZ`, `PROBLEMA`, `META`, `RELATORIO`, `LICAO_APRENDIDA`, `FORMULARIO`, `EVIDENCIA` e `OUTRO`.

Exemplo:

```bash
curl -X POST http://localhost:8000/anexos \
  -H "Authorization: Bearer <TOKEN>" \
  -F "arquivo=@./evidencia.pdf" \
  -F "id_ciclo=7" \
  -F "id_origem=9" \
  -F "categoria=EVIDENCIA" \
  -F "descricao=Evidência da verificação do resultado"
```

Resposta de recebimento:

```json
{
  "id": 42,
  "status": "PROCESSANDO"
}
```

Essa resposta não representa a confirmação final do Cloudinary. O status final deve ser consultado no fluxo de anexos do ACTA ou diretamente no banco.

### Criar anexo pela IA

```http
POST /anexos/ia
Authorization: Bearer <ACTA_IA_TOKEN>
X-Acta-Usuario-Id: <ID_DO_USUARIO>
Content-Type: multipart/form-data
```

A IA usa uma credencial própria de serviço e informa apenas o usuário em nome de quem está realizando o upload. A API valida se esse usuário está ativo, obtém a empresa diretamente de `public.usuario_sistema` e verifica se o ciclo pertence à mesma empresa. O `id_empresa` e o `firebase_uid` não são recebidos nessa rota.

Os campos do formulário e a resposta `202 Accepted` são os mesmos de `POST /anexos`.

### Consultar processamento do anexo

Para usuários autenticados:

```http
GET /anexos/{id_anexo}
Authorization: Bearer <TOKEN>
```

Para a IA:

```http
GET /anexos/ia/{id_anexo}
Authorization: Bearer <ACTA_IA_TOKEN>
X-Acta-Usuario-Id: <ID_DO_USUARIO>
```

A resposta informa o status atual, se o envio terminou com sucesso e a URL gerada pelo Cloudinary:

```json
{
  "id": 42,
  "status": "ATIVO",
  "enviado": true,
  "url": "https://res.cloudinary.com/..."
}
```

## ⚠️ Erros

O formato confirmado é:

```json
{
  "mensagens": ["campo: mensagem de validação"],
  "httpStatus": 400,
  "timestamp": "2026-09-17T10:35:00"
}
```

## 📦 Tipos de arquivo

São aceitos os seguintes formatos:

- PDF: `.pdf`
- Documentos: `.docx`, `.pptx`, `.xlsx`
- Imagens: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`, `.tif`
- Texto: `.txt`, `.csv`, `.svg`

Arquivos de texto são validados por conteúdo, incluindo UTF-8, ausência de byte nulo e estrutura básica de CSV ou SVG.

## 🔄 Processamento assíncrono

O endpoint grava o anexo com status `PROCESSANDO` e publica um `UploadJob` na fila `uploads`.

O worker:

- atualiza o status do anexo;
- envia o arquivo ao Cloudinary;
- organiza o arquivo em `acta-arquivos/{nome-empresa}-{uuid-curto}/ciclo-{id_ciclo}/{id_anexo}`;
- salva o `secure_url` retornado;
- altera o status para `ATIVO` em caso de sucesso;
- altera o status para `ERRO` em caso de falha definitiva;
- remove o arquivo temporário após o processamento concluído.

O nome da empresa é normalizado e recebe um UUID curto e estável, mantendo os anexos separados por empresa e ciclo.

Falhas de enfileiramento retornam `503`. Arquivos vazios retornam `400` e arquivos acima de 10 MB retornam `413`.

## 🧪 Testes

Execute os testes unitários com:

```bash
python -m pytest -q -p no:cacheprovider
```

Os testes usam dublês para banco, Redis e Cloudinary. Portanto, a suíte valida o comportamento interno da aplicação, mas não substitui uma validação de integração com os serviços reais.

## 📁 Estrutura

```text
.
├── app/
│   ├── database/       # Conexões PostgreSQL e Redis
│   ├── models/         # Enums e modelos relacionados
│   ├── routes/         # Endpoints HTTP
│   ├── services/       # Autenticação, fila, jobs e Cloudinary
│   ├── utils/          # Validação de arquivos
│   └── schemas.py      # Contratos de entrada e jobs
├── tests/              # Testes unitários
├── main.py             # Inicialização da API
└── worker.py           # Inicialização do worker RQ
```



## 🤝 Links e autoria

- [Repositório](https://github.com/AppActa/acta-import-api) · [Licença MIT](LICENSE) · `acta.institutojef@gmail.com`
- Contribuições: use *issues* e *pull requests*; há um [PULL_REQUEST_TEMPLATE.md](PULL_REQUEST_TEMPLATE.md).