# Pokemon API

Uma API RESTful para consulta de Pokemons, construída com FastAPI, consumindo dados da PokeAPI.

## 🚀 Tecnologias

- Python 3.11
- FastAPI
- Redis (Cache)
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Pytest (Testes)

## 📦 Funcionalidades

- ✅ Listagem paginada de Pokemons
- ✅ Busca por ID ou nome
- ✅ Cache com Redis para performance
- ✅ Rate limiting (100 requisições/minuto)
- ✅ Logs estruturados
- ✅ Documentação automática (Swagger)
- ✅ Testes unitários com cobertura
- ✅ CI/CD com GitHub Actions
- ✅ Deploy automático

## 🏠 Execução Local

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento)

## 🔐 Autenticação

A API utiliza **API Key** para autenticação nos endpoints protegidos.

### Como obter uma API Key

As API Keys são configuradas via variável de ambiente `API_KEYS` (valores separados por vírgula).

Keys padrão para desenvolvimento:
- `dev-api-key-123`
- `test-api-key-456`

### Como usar

Inclua o header `X-API-Key` em todas as requisições para endpoints protegidos:

bash
curl -H "X-API-Key: dev-api-key-123" \
  "http://localhost:8000/api/v1/pokemons?limit=5&offset=0"

### Com Docker

bash
# Clone o repositório
git clone https://github.com/bbigelli/pokemon-api.git
cd pokemon-api

# Configure as variáveis de ambiente
cp .env.example .env

# Execute com Docker Compose
docker-compose up --build

🧪 Testes

# Executar testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Ver relatório de cobertura
open htmlcov/index.html
windows
start htmlcov/index.html

📝 Endpoints
GET /api/v1/pokemons?limit=20&offset=0
Resposta:
    {
    "data": [...],
    "pagination": {
        "total": 1281,
        "limit": 20,
        "offset": 0,
        "next": "/api/v1/pokemons?limit=20&offset=20",
        "previous": null
        }
    }

Buscar Pokemon por ID
GET /api/v1/pokemons/25

Buscar Pokemon por Nome
GET /api/v1/pokemons/pikachu

📚 Documentação
Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

🌐 API em Produção
https://pokemon-api.onrender.com

🚦 CI/CD Pipeline
O pipeline é executado no GitHub Actions para:

✅ Instalação de dependências

✅ Linting (flake8)

✅ Type checking (mypy)

✅ Testes com cobertura

✅ Deploy automático no Render (branch main)

📊 Cobertura de Testes
O projeto mantém cobertura de testes > 90%, incluindo:

Endpoints

Paginação

Tratamento de erros

Cache

Rate limiting

👤 Autor
Bruno Bigelli