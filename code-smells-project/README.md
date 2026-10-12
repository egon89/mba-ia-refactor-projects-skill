# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

### Local (Python)

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

### Docker (docker compose)

```bash
docker compose up --build
```

A aplicação sobe em `http://localhost:5000`, dentro do container. O `docker-compose.yml` já define as variáveis de ambiente necessárias (ver `Dockerfile`/`docker-compose.yml` na raiz deste projeto) e persiste o SQLite num volume nomeado (`loja_data`), para que os dados sobrevivam a `docker compose down`/`up`.

Para rodar em segundo plano e ver os logs depois:

```bash
docker compose up --build -d
docker compose logs -f api
```

Para derrubar e remover o volume (reseta o banco e recria o seed no próximo `up`):

```bash
docker compose down -v
```

## Configuração

Tudo vem de variáveis de ambiente (veja `.env.example`); nenhuma é obrigatória para subir localmente.

| Variável | Padrão | Uso |
|---|---|---|
| `SECRET_KEY` | aleatória a cada boot | assina os tokens de login; defina um valor fixo fora de desenvolvimento |
| `DEBUG` | `false` | modo debug do Flask |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | endereço do servidor |
| `DB_PATH` | `loja.db` | arquivo SQLite |
| `CORS_ORIGINS` | `http://localhost:3000` | origens permitidas, separadas por vírgula |
| `TOKEN_TTL_SECONDS` | `28800` | validade do token |
| `SEED_DEMO_DATA` | `true` | cria produtos e usuários de exemplo em banco vazio |

## Autenticação

`POST /login` devolve um `token`. Envie-o como `Authorization: Bearer <token>`.

| Acesso | Rotas |
|---|---|
| Público | `GET /`, `GET /health`, `GET /produtos`, `GET /produtos/busca`, `GET /produtos/<id>`, `POST /usuarios`, `POST /login` |
| Usuário autenticado (o próprio ou admin) | `GET /usuarios/<id>`, `POST /pedidos`, `GET /pedidos/usuario/<id>` |
| Admin | `POST/PUT/DELETE /produtos`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db` |

Usuário admin de exemplo: `admin@loja.com` / `admin123` (apenas para desenvolvimento; desligue com `SEED_DEMO_DATA=false`).

## Exemplos de uso (curl)

Com a aplicação rodando em `http://localhost:5000` (local ou via Docker), e usando o usuário admin de exemplo (`admin@loja.com` / `admin123`, criado pelo seed quando `SEED_DEMO_DATA=true`).

### Rotas públicas

```bash
# Healthcheck
curl http://localhost:5000/health

# Listar produtos
curl http://localhost:5000/produtos

# Buscar produtos (filtros opcionais)
curl "http://localhost:5000/produtos/busca?q=notebook&preco_min=1000&preco_max=5000"

# Buscar produto por id
curl http://localhost:5000/produtos/1

# Criar usuário
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nome": "Maria Silva", "email": "maria@example.com", "senha": "senha-forte-123"}'
```

### Login e uso do token

```bash
# Login (admin de exemplo) — guarda o token numa variável de shell
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@loja.com", "senha": "admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "$TOKEN"
```

### Rotas autenticadas (próprio usuário ou admin)

```bash
# Buscar o próprio usuário (id 1 = admin de exemplo)
curl http://localhost:5000/usuarios/1 \
  -H "Authorization: Bearer $TOKEN"

# Criar pedido
curl -X POST http://localhost:5000/pedidos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": 2}]}'

# Listar pedidos de um usuário
curl http://localhost:5000/pedidos/usuario/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Rotas de admin

```bash
# Criar produto (categorias válidas: informatica, moveis, vestuario, geral, eletronicos, livros)
curl -X POST http://localhost:5000/produtos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"nome": "Teclado Mecânico", "descricao": "Switches azuis", "preco": 349.90, "estoque": 20, "categoria": "eletronicos"}'

# Atualizar produto (id 1)
curl -X PUT http://localhost:5000/produtos/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"nome": "Teclado Mecânico v2", "preco": 329.90, "estoque": 15, "categoria": "eletronicos"}'

# Deletar produto (id 1)
curl -X DELETE http://localhost:5000/produtos/1 \
  -H "Authorization: Bearer $TOKEN"

# Listar usuários
curl http://localhost:5000/usuarios \
  -H "Authorization: Bearer $TOKEN"

# Listar todos os pedidos
curl http://localhost:5000/pedidos \
  -H "Authorization: Bearer $TOKEN"

# Atualizar status de um pedido (id 1)
curl -X PUT http://localhost:5000/pedidos/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "aprovado"}'

# Relatório de vendas
curl http://localhost:5000/relatorios/vendas \
  -H "Authorization: Bearer $TOKEN"
```

> Todas as rotas de admin/autenticadas respondem `401` sem o header `Authorization`, e `403` quando o token é de um usuário sem permissão — é o gate de autenticação criado na Fase 3 da skill `refactor-arch` (ver seção "Autenticação" acima).

## Estrutura

```
app.py                 # entry point: cria o app e sobe o servidor
src/
├── app.py             # composition root (create_app)
├── config/            # settings (env) e regras de negócio nomeadas
├── database/          # conexão por requisição, schema e seed
├── models/            # acesso a dados parametrizado, um módulo por entidade
├── services/          # regras de negócio (pedido, relatório, auth, notificação)
├── controllers/       # orquestração da requisição
├── views/             # blueprints: declaração de rotas
├── middlewares/       # autenticação e tratamento de erro central
└── utils/             # exceções e validadores
```
