# task-manager-api

API de Task Manager em Python/Flask, organizada em camadas MVC:

```
app.py          composition root (create_app)
config/         settings lidos do ambiente + constantes de domínio
models/         entidades SQLAlchemy
services/       regras de negócio e consultas
controllers/    orquestração da requisição
views/          formatos de resposta
routes/         blueprints (só declaração de rotas)
middlewares/    autenticação e tratamento de erro central
utils/          erros, validadores, helpers
```

## Como rodar

### Local (Python)

```bash
pip install -r requirements.txt
cp .env.example .env   # defina SECRET_KEY
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

Sem `SECRET_KEY` definida, a aplicação gera uma chave temporária a cada boot e os tokens emitidos deixam de valer ao reiniciar.

### Docker (docker compose)

```bash
docker compose up --build
```

A aplicação sobe em `http://localhost:5000`, dentro do container. O `docker-compose.yml` já define as variáveis de ambiente necessárias e o comando do container roda `python seed.py && python app.py` — ou seja, cada `docker compose up` recria o banco do zero com os dados de exemplo (não há volume para persistir dados entre subidas, assim como no uso local com `python seed.py`).

Para rodar em segundo plano e ver os logs depois:

```bash
docker compose up --build -d
docker compose logs -f api
```

Para derrubar:

```bash
docker compose down
```

## Autenticação

`GET /`, `GET /health`, `POST /login` e `POST /users` (cadastro com role `user`) são públicas. As demais rotas exigem o token devolvido pelo login:

```bash
curl -X POST localhost:5000/login -H 'Content-Type: application/json' \
  -d '{"email":"joao@email.com","password":"1234"}'
curl localhost:5000/tasks -H 'Authorization: Bearer <token>'
```

- `PUT /users/<id>`: o próprio usuário ou um admin; alterar `role`/`active` só admin.
- `DELETE /users/<id>` e criação de usuário com role `admin`/`manager`: só admin.

## Exemplos de uso (curl)

Com a aplicação rodando em `http://localhost:5000` (local ou via Docker), usando o usuário admin de exemplo criado pelo seed (`joao@email.com` / `1234`).

### Rotas públicas

```bash
# Healthcheck
curl http://localhost:5000/health

# Login — guarda o token numa variável de shell
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@email.com", "password": "1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "$TOKEN"

# Cadastro de usuário (role padrão "user")
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Nova Usuária", "email": "nova@email.com", "password": "senha123"}'
```

### Tasks (autenticado)

```bash
# Listar tasks
curl http://localhost:5000/tasks \
  -H "Authorization: Bearer $TOKEN"

# Criar task
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Testar Docker", "description": "Validar compose", "status": "pending", "priority": 2, "user_id": 1, "category_id": 1}'

# Buscar tasks (filtros opcionais: q, status, priority, user_id)
curl "http://localhost:5000/tasks/search?q=docker" \
  -H "Authorization: Bearer $TOKEN"

# Estatísticas de tasks
curl http://localhost:5000/tasks/stats \
  -H "Authorization: Bearer $TOKEN"

# Atualizar task (id 1)
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "done"}'

# Deletar task (id 1)
curl -X DELETE http://localhost:5000/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Categorias (autenticado)

```bash
# Listar categorias
curl http://localhost:5000/categories \
  -H "Authorization: Bearer $TOKEN"

# Criar categoria
curl -X POST http://localhost:5000/categories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "QA", "description": "Tarefas de qualidade", "color": "#9b59b6"}'
```

### Usuários e relatórios (autenticado / admin)

```bash
# Listar usuários
curl http://localhost:5000/users \
  -H "Authorization: Bearer $TOKEN"

# Tasks de um usuário
curl http://localhost:5000/users/1/tasks \
  -H "Authorization: Bearer $TOKEN"

# Deletar usuário (id 2, somente admin)
curl -X DELETE http://localhost:5000/users/2 \
  -H "Authorization: Bearer $TOKEN"

# Relatório geral
curl http://localhost:5000/reports/summary \
  -H "Authorization: Bearer $TOKEN"

# Relatório de um usuário
curl http://localhost:5000/reports/user/1 \
  -H "Authorization: Bearer $TOKEN"
```

> Todas as rotas acima (exceto `/health`, `/login` e `POST /users`) respondem `401` sem o header `Authorization`, e `403` quando a operação exige papel de admin e o token é de outro usuário.
