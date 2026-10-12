# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express, refatorada para MVC pela skill `refactor-arch`.

## Como rodar

### Local (Node.js)

```bash
npm install
cp .env.example .env   # defina ADMIN_API_TOKEN
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória por padrão e já carrega seeds automaticamente no boot.

### Docker (docker compose)

```bash
docker compose up --build
```

A aplicação sobe em `http://localhost:3000`, dentro do container. O `docker-compose.yml` já define `ADMIN_API_TOKEN`/`PAYMENT_GATEWAY_KEY` de desenvolvimento e mantém `DB_FILE=:memory:` — como o banco é em memória, cada `docker compose up` recria o container com os seeds do zero (não há volume para persistir dados entre subidas).

Para rodar em segundo plano e ver os logs depois:

```bash
docker compose up --build -d
docker compose logs -f api
```

Para derrubar:

```bash
docker compose down
```

Exemplos de requisições estão em `api.http` e na seção "Exemplos de uso (curl)" abaixo.

## Configuração

| Variável | Padrão | Uso |
|---|---|---|
| `PORT` | `3000` | Porta HTTP |
| `ADMIN_API_TOKEN` | — | Token exigido em `Authorization: Bearer <token>` nas rotas administrativas. Sem ele, essas rotas respondem 401. |
| `PAYMENT_GATEWAY_KEY` | — | Chave do gateway de pagamento (o gateway atual é simulado) |
| `DB_FILE` | `:memory:` | Arquivo SQLite |

## Rotas

| Método | Path | Autenticação |
|---|---|---|
| `POST` | `/api/checkout` | pública |
| `GET` | `/api/admin/financial-report` | token de admin |
| `DELETE` | `/api/users/:id` | token de admin |

## Exemplos de uso (curl)

Com a aplicação rodando em `http://localhost:3000` (local ou via Docker). Os exemplos de token de admin usam o valor de desenvolvimento definido no `docker-compose.yml` (`dev-admin-token-change-me`) — ajuste para o valor do seu `.env` se estiver rodando localmente.

### Checkout (rota pública)

```bash
# Checkout com sucesso (cartão iniciado em "4" é aprovado pelo gateway simulado)
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr": "Guilherme", "eml": "gui@fullcycle.com.br", "pwd": "senhaforte", "c_id": 2, "card": "4111222233334444"}'

# Checkout com pagamento recusado (cartão não iniciado em "4")
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr": "Joao", "eml": "joao@teste.com", "pwd": "123", "c_id": 1, "card": "5111222233334444"}'
```

### Rotas administrativas (exigem `ADMIN_API_TOKEN`)

```bash
TOKEN=dev-admin-token-change-me

# Relatório financeiro
curl http://localhost:3000/api/admin/financial-report \
  -H "Authorization: Bearer $TOKEN"

# Deletar usuário (também remove matrículas e pagamentos associados)
curl -X DELETE http://localhost:3000/api/users/1 \
  -H "Authorization: Bearer $TOKEN"
```

> As rotas administrativas respondem `401` sem o header `Authorization` ou com um token inválido — é o gate de autenticação construído na Fase 3 da skill `refactor-arch` (ver seção "Configuração" acima; antes da refatoração essas rotas não exigiam nenhuma autenticação).

## Estrutura

```
src/
├── app.js          # composition root
├── config/         # variáveis de ambiente e regras de negócio nomeadas
├── database/       # conexão (Promises + transação), schema e seed
├── models/         # acesso a dados, um módulo por entidade
├── services/       # checkout, pagamento, relatório, usuário, hash de senha
├── controllers/    # validação de entrada e resposta HTTP
├── routes/         # declaração das rotas
├── middlewares/    # autenticação de admin e error handler central
└── utils/          # erros de aplicação e asyncHandler
```
