# Pokemon API - Projeto Final Backend Python

## 📋 Descrição

API RESTful completa que integra:
- **Consulta à PokeAPI** com cache Redis
- **CRUD completo** com banco de dados PostgreSQL (SQLAlchemy)
- **Autenticação** por API Key
- **Rate limiting** e logs estruturados
- **Docker** e CI/CD com GitHub Actions

## 🗄️ Endpoints CRUD (Banco de Dados)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/favorites` | Adicionar pokemon aos favoritos |
| GET | `/api/v1/favorites` | Listar favoritos (paginado) |
| GET | `/api/v1/favorites/{id}` | Buscar favorito por ID do banco |
| GET | `/api/v1/favorites/pokemon/{id}` | Buscar favorito por ID da PokeAPI |
| PUT | `/api/v1/favorites/{id}` | Atualizar favorito (nickname, notas) |
| DELETE | `/api/v1/favorites/{id}` | Remover dos favoritos |

## 🔍 Endpoints de Consulta (PokeAPI)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/public/pokemons` | Listar pokemons (público) |
| GET | `/api/v1/pokemons` | Listar pokemons (requer API Key) |
| GET | `/api/v1/pokemons/{id}` | Buscar pokemon por ID (requer API Key) |

## 🚀 Como executar

bash
# Clone o repositório
git clone https://github.com/bbigelli/pokemon-api.git
cd pokemon-api

# Configure as variáveis de ambiente
cp .env.example .env

# Execute com Docker Compose
docker-compose up --build

### Autor

Bruno Bigelli

