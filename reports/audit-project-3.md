# Audit — task-manager-api

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (3.10.12 no ambiente local)
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1, flask-cors 4.0.0, marshmallow 3.20.1, requests 2.31.0, python-dotenv 1.0.0
Domain:        API de gerenciamento de tarefas (tasks, usuários, categorias, relatórios, login)
Architecture:  parcialmente organizada — existem models/, routes/, services/ e utils/, mas as rotas acumulam validação, acesso ao ORM, regra de negócio e serialização; não há camada de controller/service em uso
Source files:  15 files analyzed
DB tables:     users, categories, tasks (tasks.user_id -> users, tasks.category_id -> categories) — SQLite via SQLAlchemy
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1 / SQLite)
Files:   15 analisados | ~1158 linhas de código

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Segredos hardcoded e debug/CORS inseguros (AP-02)
File: app.py:13, app.py:15, app.py:34, services/notification_service.py:9-10
Description:
  - app.py:13 — SECRET_KEY literal 'super-secret-key-123'
  - app.py:34 — app.run(debug=True, host='0.0.0.0'): debugger Werkzeug exposto em todas as interfaces
  - app.py:15 — CORS(app) sem restrição de origem
  - services/notification_service.py:9-10 — usuário e senha SMTP ('senha123') no código
  - app.py:11 — URI do banco fixa no código; python-dotenv está no manifesto mas nunca é usado
Impact: segredos versionados vazam com o repositório; debug=True em 0.0.0.0 permite execução remota de código pelo console do debugger.
Recommendation: RP-01 — config/ lendo variáveis de ambiente, DEBUG default false, CORS restrito a origens configuradas.

### [CRITICAL] Exposição de hash de senha nas respostas (AP-04)
File: models/user.py:21
Description: User.to_dict() inclui 'password'. O dicionário é devolvido em:
  - routes/user_routes.py:33 — GET /users/<id>
  - routes/user_routes.py:85 — POST /users
  - routes/user_routes.py:129 — PUT /users/<id>
  - routes/user_routes.py:209 — POST /login
Impact: qualquer chamador anônimo obtém o hash de qualquer usuário via GET /users/<id>; combinado com MD5 (finding seguinte), equivale a expor a senha.
Recommendation: RP-04 — serializador que nunca inclui o campo password. Breaking change de segurança.

### [CRITICAL] Hash de senha com MD5 sem salt (AP-05)
File: models/user.py:29, models/user.py:32
Description: set_password e check_password usam hashlib.md5(pwd).hexdigest(), sem salt.
Impact: MD5 é quebrável por tabela/força bruta em segundos; um vazamento do banco (ou do finding anterior) revela as senhas originais.
Recommendation: RP-05 — werkzeug.security.generate_password_hash / check_password_hash. Hashes MD5 já gravados precisam de re-seed ou migração no próximo login.

### [HIGH] Autenticação fictícia e autorização ausente (AP-08)
File: routes/user_routes.py:210
Description:
  - routes/user_routes.py:210 — token 'fake-jwt-token-' + id, previsível e não assinado
  - nenhuma rota exige credencial: a busca por Authorization/headers/jwt/before_request/login_required só retorna a linha 210
  - models/user.py:34 — is_admin() existe e nunca é chamado
  - routes/user_routes.py:52, 71-78 e 119-122 — qualquer chamador cria ou promove usuário para role 'admin'
  - rotas destrutivas públicas: DELETE /users/<id> (user_routes.py:134), DELETE /tasks/<id> (task_routes.py:225), DELETE /categories/<id> (report_routes.py:211)
Impact: qualquer pessoa lê, altera e apaga dados de qualquer usuário e se autoconcede admin.
Recommendation: RP-08 — token assinado com expiração, middleware de autenticação em todas as rotas sensíveis, checagem de papel para operações administrativas. Breaking change de segurança.

### [HIGH] Rotas acumulando controller, service e repositório (AP-06)
File: routes/task_routes.py:1-299, routes/user_routes.py:1-211, routes/report_routes.py:1-223
Description: cada handler faz parsing HTTP, validação, consulta ORM, regra de negócio, agregação e serialização no mesmo corpo. Exemplos: create_task (task_routes.py:85-154), update_task (task_routes.py:156-223), summary_report (report_routes.py:12-101). O CRUD de categorias mora dentro do módulo de relatórios (report_routes.py:157-223). app.py:30-31 executa db.create_all() no import, sem app factory.
Impact: nada é testável sem subir HTTP + banco; qualquer mudança de regra mexe em handler de rota.
Recommendation: RP-06 — separar em routes (HTTP) → controllers → services → models; blueprint próprio para categorias; create_app() como composition root.

### [HIGH] Regra "task atrasada" reimplementada em 6 pontos (AP-07)
File: routes/task_routes.py:30-39, 71-80, 284-287; routes/user_routes.py:171-180; routes/report_routes.py:34-36, 132-135
Description: a mesma condição (due_date < agora e status fora de done/cancelled) é copiada em 6 lugares, enquanto Task.is_overdue() (models/task.py:50-60) nunca é chamado. O mesmo vale para o cálculo de completion_rate (task_routes.py:296, report_routes.py:67 e 151), que ignora calculate_percentage (utils/helpers.py:14).
Impact: regra de negócio duplicada diverge silenciosamente; alterar a definição de "atrasada" exige achar as 6 cópias.
Recommendation: RP-07 — fonte única (Task.is_overdue / service de tasks) chamada por todas as rotas.

### [MEDIUM] Queries N+1 e contagens em série (AP-10)
File: routes/task_routes.py:42, routes/task_routes.py:51
Description:
  - task_routes.py:42 e 51 — User.query.get e Category.query.get por task em GET /tasks (os relationships já existem em models/task.py:20-21)
  - user_routes.py:22 — len(u.tasks) dispara um lazy load por usuário em GET /users
  - report_routes.py:56 — uma query de tasks por usuário em /reports/summary
  - report_routes.py:163 — um COUNT por categoria em GET /categories
  - task_routes.py:275-281 e report_routes.py:15-30 — 5 e 12 COUNTs separados, mais carga da tabela inteira para contar atrasadas
Impact: o número de round-trips cresce linearmente com tasks/usuários/categorias.
Recommendation: RP-10 — joinedload/JOIN e agregações com GROUP BY.

### [MEDIUM] Validação/serialização duplicada e código morto (AP-11)
File: routes/task_routes.py:96-114 vs 167-184
Description:
  Duplicação:
  - validação de task copiada entre create e update (task_routes.py:96-114 / 167-184), com mensagens de data divergentes (138 vs 205)
  - regex de e-mail em user_routes.py:61 e 106, ignorando validate_email (utils/helpers.py:19)
  - serialização manual de task em task_routes.py:17-28 e user_routes.py:162-169, ignorando Task.to_dict (models/task.py:23)
  Código morto:
  - services/notification_service.py:1-48 — nunca importado
  - utils/helpers.py — process_task_data (57), validate_email (19), sanitize_string (25), generate_id (31), log_action (36), parse_date (43), is_valid_color (52), constantes (110-116)
  - report_routes.py:7 — importa format_date e calculate_percentage e não usa
  - models/task.py:38 e 45 (validate_status, validate_priority), models/user.py:34 (is_admin)
  - imports sem uso: app.py:7 (os, sys, json), task_routes.py:7, user_routes.py:6 (hashlib, json), report_routes.py:8, models/task.py:3, utils/helpers.py:3-7
  - requirements.txt:4-6 — marshmallow, requests e python-dotenv não são importados
Impact: regras já divergem entre criar e atualizar; utilitários mortos sugerem validações que não acontecem.
Recommendation: RP-11 — um validador e um serializador por entidade; remover o que está comprovadamente morto.

### [MEDIUM] APIs deprecated (AP-12)
File: routes/task_routes.py:42 (e mais 15 ocorrências), models/task.py:15-16 (e mais 19 ocorrências)
Description: ver seção "Deprecated APIs".
Impact: LegacyAPIWarning do SQLAlchemy 2.x e DeprecationWarning do Python 3.12+; candidatos a remoção.
Recommendation: RP-12.

### [LOW] Magic numbers e listas inline (AP-13)
File: routes/task_routes.py:110
Description:
  - lista de status repetida em task_routes.py:110 e 177, models/task.py:39, utils/helpers.py:75 e 110
  - lista de roles em user_routes.py:71 e 120
  - limites sem nome: título 3/200 (task_routes.py:96, 99, 167, 169), prioridade 1-5 (113, 182), senha 4 (user_routes.py:64, 115), janela de 7 dias (report_routes.py:45), "alta prioridade" <= 2 (report_routes.py:129)
  - variáveis de uma letra em fluxo de negócio (t, u, c, p1..p5)
Impact: intenção implícita; as constantes de utils/helpers.py:110-116 existem mas ninguém as usa.
Recommendation: RP-13 — constantes nomeadas em um único módulo.

### [LOW] Tratamento de erro genérico e inconsistente (AP-14)
File: routes/task_routes.py:62
Description: variante do padrão — aqui o erro não vaza str(e) ao cliente, ele é engolido.
  - 12 `except:` nus: task_routes.py:62, 137, 204, 236; user_routes.py:130, 149; report_routes.py:186, 207, 221; utils/helpers.py:46, 49, 88
  - sem error handler central: exceções não capturadas devolvem a página HTML padrão do Flask, não JSON
  - entradas que geram 500: priority não numérico (task_routes.py:113, 182), title não string (96, 167), ?priority=abc ou ?user_id=abc na busca (261, 264), PUT /categories sem corpo JSON (report_routes.py:197)
  - log via print (ex.: task_routes.py:149, user_routes.py:89)
Impact: erros reais ficam invisíveis e o cliente recebe formatos de erro diferentes por rota.
Recommendation: RP-14 — error handler central com logging; validar tipos na entrada.

## Deprecated APIs
- Model.query.get(id) — legado no SQLAlchemy 2.x (exigido pelo Flask-SQLAlchemy 3.1.1); equivalente: db.session.get(Model, id). 16 ocorrências:
  routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227
  routes/user_routes.py:29, 94, 136, 155
  routes/report_routes.py:105, 192, 213
- datetime.utcnow() — deprecated a partir do Python 3.12; equivalente: datetime.now(timezone.utc). 22 ocorrências em 9 arquivos:
  models/task.py (3), models/user.py (1), models/category.py (1), routes/task_routes.py (4), routes/user_routes.py (1), routes/report_routes.py (5), services/notification_service.py (1), utils/helpers.py (1), seed.py (5)

Checados e ausentes: AP-01 (sem SQL bruto; o like(f'%{query}%') de task_routes.py:252-253 é parâmetro vinculado pelo ORM), AP-03 (nenhum endpoint de execução arbitrária ou reset de banco) e AP-09 (db = SQLAlchemy() é o padrão da extensão; a lista em memória do NotificationService é por instância e está em código morto).

================================
Total: 11 findings
================================
```

Os caminhos e linhas acima se referem ao código anterior à refatoração (`services/notification_service.py` e `utils/helpers.py` foram removidos; os três arquivos de `routes/` foram reescritos).

## Resultado da Refatoração

- **Estrutura MVC criada:** melhoria direcionada sobre as pastas existentes (projeto já parcialmente em camadas). `app.py` (composition root, `create_app`) + `config/` (settings do ambiente, constantes de domínio), `models/` (task, user, category — mantidos, com correções), `services/` (task, user, category, report, auth), `controllers/` (task, user, category, report, auth), `views/` (formatos de resposta de task, user, category), `routes/` (5 blueprints só com declaração de rota; categorias e login ganharam blueprint próprio), `middlewares/` (auth, error_handler), `utils/` (errors, validators, clock, metrics). 40 arquivos `.py`, 1254 linhas; `routes/` caiu de 734 para 59 linhas. `.env.example` adicionado. `requirements.txt` perdeu `marshmallow` e `requests` (nunca importados); nenhuma dependência nova (token assinado usa `itsdangerous`, hash usa `werkzeug`, ambos já instalados pelo Flask).
- **Validação:**
  - Boot com `python seed.py` + `python app.py` sem erro nem warning de deprecation no log (`Debug mode: off`, `Running on http://127.0.0.1:<PORT>`).
  - 68 chamadas da linha de base repetidas com token de admin: 62 idênticas em status e corpo (ignorando timestamps, valor do token e o campo `password` removido). As 6 diferentes são todas casos de erro: `priority` não numérico, `title` não string e `?priority=abc` (500 HTML → 400 JSON); `PUT /categories/1` e `POST /tasks` sem corpo JSON (415 HTML → 400 `Dados inválidos`); rota inexistente (404 HTML → 404 JSON).
  - Mesmas 68 chamadas sem token: só `GET /`, `GET /health`, `POST /login` e `POST /users` respondem; todo o resto devolve 401.
  - Autorização: usuário comum recebe 403 em `DELETE /users/<id>`, em `PUT` de outro usuário e ao tentar mudar o próprio `role`; anônimo recebe 403 ao criar usuário com role `admin`; admin consegue. Token antigo `fake-jwt-token-1`, token adulterado e token expirado devolvem 401. Usuário desativado perde o token (401) e o login (403).
  - Senhas gravadas como `scrypt:32768:8:1$...`; um hash MD5 antigo no banco falha a verificação sem erro 500.
  - Sinais de detecção reexecutados: 0 `Model.query.get`, 0 `datetime.utcnow`, 0 `except:` nu, 0 segredos literais, 0 `md5`, 0 `debug=True`/`0.0.0.0`; nenhum acesso a ORM em controllers/routes/views; nenhum uso de `flask.request` em services/models; `pyflakes` limpo exceto os reexports de `__init__.py`.
- **Findings CRITICAL/HIGH resolvidos:** 6/6. MEDIUM/LOW: 5/5.
- **Breaking changes de segurança:**
  - O campo `password` saiu das respostas de `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
  - `POST /login` devolve um token assinado com expiração (8 h por padrão) em vez de `fake-jwt-token-<id>`.
  - Todas as rotas de tasks, categorias, relatórios e usuários (exceto `POST /users`) exigem `Authorization: Bearer <token>`; sem ele, 401.
  - `DELETE /users/<id>` só para admin. `PUT /users/<id>` só para o próprio usuário ou admin; alterar `role`/`active` só admin.
  - `POST /users` continua público, mas `role` diferente de `user` exige token de admin (403 caso contrário).
  - CORS deixou de ser aberto: só as origens listadas em `CORS_ORIGINS` (vazio por padrão).
  - `python app.py` sobe em `127.0.0.1` com debug desligado; `HOST`, `PORT` e `DEBUG` vêm do ambiente.
  - Hashes MD5 existentes deixam de autenticar: é preciso rodar `python seed.py` de novo (ou redefinir as senhas).
- **Outras mudanças de comportamento:**
  - Erros não tratados e 404/405 de rota respondem JSON `{"error": ...}` em vez de HTML.
  - Corpo ausente ou não JSON responde 400 `Dados inválidos` em vez de 415.
  - `PUT /tasks/<id>` com data inválida responde a mesma mensagem do `POST` (`Formato de data inválido. Use YYYY-MM-DD`).
  - `PUT /users/<id>` com `name` vazio ou `active` não booleano responde 400.
  - `services/notification_service.py` (nunca chamado) foi removido, junto com as credenciais SMTP que continha.
