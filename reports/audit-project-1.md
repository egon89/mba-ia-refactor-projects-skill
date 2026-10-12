# Audit — code-smells-project

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1 (sqlite3 bruto, sem ORM)
Files:   4 analisados | ~780 linhas de código

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] SQL Injection por concatenação de string (AP-01)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155, 157-161, 163-166, 174, 188, 192, 220, 224, 279-281, 291-299
Description: 19 chamadas cursor.execute em models.py montam SQL por concatenação; só as queries sem parâmetro são seguras. Pontos alcançáveis com entrada livre do cliente:
  - models.py:109-111 — login: email/senha do body direto no WHERE.
  - models.py:291-299 — busca: q e categoria da query string.
  - models.py:47-50, 57-61, 126-129 — INSERT/UPDATE com strings do body.
  - models.py:140, 148-151, 155-166 — usuario_id, produto_id, quantidade do JSON, sem checagem de tipo.
  (28, 68, 92, 174 recebem <int:...> da rota, então não eram exploráveis, mas seguiam o mesmo padrão.)
Impact: bypass de autenticação em POST /login (' OR '1'='1), leitura de usuarios.senha via UNION em GET /produtos/busca, e alteração ou destruição de dados.
Recommendation: placeholders ? + tupla de parâmetros em todas as queries, inclusive a busca dinâmica (RP-02).

### [CRITICAL] Segredos hardcoded e debug/CORS inseguros (AP-02)
File: app.py:7, app.py:8, app.py:9, app.py:88, controllers.py:289
Description: SECRET_KEY literal (app.py:7, repetida em controllers.py:289); DEBUG = True fixo (app.py:8) e app.run(host="0.0.0.0", debug=True) (app.py:88); CORS(app) sem restrição de origem (app.py:9). O app se declara "producao" (controllers.py:286).
Impact: segredo versionado no git; o debugger do Werkzeug exposto em 0.0.0.0 permite execução remota de código; qualquer origem pode chamar a API.
Recommendation: config/settings.py lendo env vars, DEBUG default false, CORS restrito a origens configuradas (RP-01).

### [CRITICAL] Endpoint de execução arbitrária (AP-03)
File: app.py:59-78, app.py:47-57
Description: POST /admin/query executa o SQL recebido em dados["sql"] (app.py:69) sem autenticação. POST /admin/reset-db apaga as 4 tabelas (app.py:51-54), também sem autenticação.
Impact: qualquer chamador de rede tem controle total do banco.
Recommendation: remover /admin/query; manter /admin/reset-db só atrás de autenticação + papel admin (RP-03).

### [CRITICAL] Exposição de dado sensível na resposta/log (AP-04)
File: models.py:83, models.py:99, controllers.py:285-289
Description: GET /usuarios e GET /usuarios/<id> devolvem o campo senha (models.py:83, 99). GET /health devolve secret_key, debug e db_path (controllers.py:287-289).
Impact: um GET público lista todas as senhas, e outro entrega a chave da aplicação.
Recommendation: serializador de usuário sem senha; health sem segredos nem detalhe interno (RP-04).

### [CRITICAL] Senha em texto plano (AP-05)
File: models.py:109-111, models.py:126-129, database.py:76-78, database.py:31
Description: senha gravada como recebida (models.py:126-129), comparada em texto plano no SQL (models.py:109-111), seed com senhas em claro (database.py:76-78).
Impact: qualquer leitura do banco expõe todas as senhas originais.
Recommendation: werkzeug.security generate_password_hash/check_password_hash; login busca por email e verifica o hash em Python; seed com hash (RP-05).

### [HIGH] God Module (AP-06)
File: models.py:1-314, database.py:7-86, app.py:47-78
Description: models.py concentra persistência, serialização e regra de negócio de 4 domínios. get_db() abre conexão, cria schema e faz seed na mesma função (database.py:7-86). app.py, que deveria ser composition root, contém handlers com SQL (app.py:47-78).
Impact: sem separação por domínio, nada é testável em isolamento.
Recommendation: dividir em models/controllers/services/routes por domínio, com schema e seed fora da conexão (RP-06).

### [HIGH] Lógica de negócio na camada errada (AP-07)
File: models.py:133-169, models.py:256-262, controllers.py:208-210, controllers.py:247-250, controllers.py:264-274
Description: o model calcula total e valida/baixa estoque (models.py:133-169) e aplica a faixa de desconto do relatório (models.py:256-262). O controller dispara "notificações" (controllers.py:208-210, 247-250) e executa SQL no health check (controllers.py:264-274). O texto em controllers.py:250 diz "Devolver estoque", mas nenhum código devolve.
Impact: regras de pedido e desconto não são reutilizáveis nem testáveis sem banco; cancelamento não restitui estoque.
Recommendation: services/ para pedido, relatório e notificação; models só persistem (RP-07).

### [HIGH] Autenticação e autorização ausentes (AP-08)
File: app.py:11-30, app.py:47, app.py:59, controllers.py:167-186, models.py:122
Description: nenhuma das 18 rotas exige credencial. POST /login devolve os dados do usuário sem emitir token (controllers.py:180). O campo tipo (admin/cliente) existe (models.py:122) mas nunca é verificado.
Impact: qualquer pessoa cria/apaga produtos, lê pedidos de qualquer usuário, altera status de pedido e vê o relatório de vendas.
Recommendation: token assinado com expiração emitido no login e decorators login_required/admin_required nas rotas sensíveis (RP-08).

### [HIGH] Estado global mutável (AP-09)
File: database.py:4, database.py:8-10
Description: conexão única em variável de módulo (db_connection, database.py:4), mutada via global e aberta com check_same_thread=False (database.py:10), compartilhada por todas as requisições.
Impact: condição de corrida sob concorrência; sem rollback em erro, escritas não confirmadas de uma requisição (ex.: falha no meio de criar_pedido, models.py:148-166) são gravadas pelo commit da requisição seguinte.
Recommendation: conexão por requisição via flask.g + teardown, com rollback em exceção (RP-09).

### [MEDIUM] Queries N+1 (AP-10)
File: models.py:186-192, models.py:219-224, models.py:139-140, models.py:154-155, models.py:239-254
Description: listagem de pedidos faz 1 query por pedido para itens e 1 por item para o nome do produto (models.py:186-192 e 219-224). criar_pedido consulta cada produto duas vezes (models.py:140 e 155). O relatório faz 5 queries de agregação separadas (models.py:239-254).
Impact: GET /pedidos custa 1 + P + I round-trips e não tem paginação.
Recommendation: JOIN único pedidos/itens_pedido/produtos agrupado em memória; agregação em uma query (RP-10).

### [MEDIUM] Validação/serialização duplicada e código morto (AP-11)
File: controllers.py:28-50, controllers.py:72-90, models.py:12-21, models.py:31-40, models.py:304-313, models.py:178-201, models.py:211-233, models.py:2, database.py:2
Description:
  - Validação de produto copiada entre criar (controllers.py:28-50) e atualizar (72-90), já divergente: o update não valida tamanho do nome nem categoria.
  - Serialização de produto repetida 3x (models.py:12-21, 31-40, 304-313); a de pedido + itens, 2x (178-201, 211-233).
  - Imports não usados: sqlite3 (models.py:2), os (database.py:2). A coluna ativo (database.py:22) nunca é filtrada.
Impact: regras divergem entre criar e atualizar; cada mudança de campo exige editar várias cópias.
Recommendation: um validador e um serializador por entidade; remover imports mortos (RP-11).

### [LOW] Magic numbers e listas inline (AP-13)
File: models.py:257-262, controllers.py:47, controllers.py:49, controllers.py:52, controllers.py:242, app.py:36, controllers.py:285, app.py:88
Description: faixas de desconto 10000/5000/1000 e 0.1/0.05/0.02 (models.py:257-262); limites 2 e 200 do nome (controllers.py:47, 49); categorias e status válidos inline (controllers.py:52, 242); versão "1.0.0" em dois lugares (app.py:36, controllers.py:285); porta 5000 fixa (app.py:88).
Impact: intenção implícita, e mudar uma regra exige caçar literais.
Recommendation: constantes nomeadas em config/ (RP-13).

### [LOW] Tratamento de erro genérico que vaza detalhe interno (AP-14)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292; app.py:77-78
Description: 17 blocos except Exception as e devolvem str(e) ao cliente (16 em controllers.py, 1 em app.py). Erros de entrada viram 500: float() inválido na busca (controllers.py:119-121) e body ausente no login (controllers.py:170). Há 19 print() no lugar de logging (14 em controllers.py, 5 em app.py).
Impact: mensagens de erro do SQLite chegam ao cliente e ajudam a explorar o AP-01; erros de cliente são reportados como falha do servidor.
Recommendation: error handler central que loga internamente e responde mensagem padronizada; logging no lugar de print (RP-14).

## Deprecated APIs
Nenhuma API deprecated detectada. Verificado: Flask 3.1.1 (sem before_first_request, flask.json.JSONEncoder, FLASK_ENV ou _request_ctx_stack), flask-cors 5.0.1 e sqlite3 da stdlib (os adapters/converters de data deprecated no Python 3.12 não são usados, pois não há detect_types).

================================
Total: 13 findings
================================
```

Os caminhos e linhas acima se referem ao código legado anterior à refatoração (commit `104c584`: `app.py`, `controllers.py`, `models.py`, `database.py`, todos removidos ou substituídos).

## Resultado da Refatoração

- **Estrutura MVC criada:** `app.py` (entry point) + `src/` com `app.py` (composition root, `create_app`), `config/` (settings por env, regras de negócio nomeadas), `database/` (conexão por requisição, schema/seed), `models/` (produto, usuario, pedido, manutencao), `services/` (produto, usuario, auth, pedido, relatorio, notification, admin, health), `controllers/` (produto, usuario, pedido, relatorio, admin, home), `views/` (6 blueprints), `middlewares/` (auth, error_handler), `utils/` (errors, validators, http). 44 arquivos `.py`, 1151 linhas. `controllers.py`, `models.py` e `database.py` legados foram removidos.
- **Validação:**
  - Boot com `python app.py` sem erro, 0 tracebacks no log.
  - 35 chamadas da linha de base repetidas com token de admin: 20 respostas idênticas, 15 diferentes, todas esperadas — 5 mudanças de segurança (`/health` 2x, `/usuarios`, `/usuarios/2`, `/admin/query` → 404), 2 logins com o campo `token` a mais, 6 erros 4xx com `"sucesso": false` a mais, e 2 ataques de SQL injection que deixaram de funcionar (login `' OR '1'='1` 200 → 401; busca com UNION 500 → 200 com lista vazia).
  - Autorização: 11 rotas protegidas respondem 401 sem token, token forjado 401, token de cliente 403 em rotas de admin e em dados de outro usuário.
  - Pedido que falha no meio é revertido por inteiro (estoque e pedidos inalterados).
  - Banco legado com senha em texto plano é convertido para hash no boot e o login continua funcionando.
  - Sinais de detecção reexecutados: sem concatenação de valor em SQL, sem segredo/debug hardcoded, sem `global`, sem `str(e)` em resposta, sem `print`, SQL só em `models/` e `database/`.
- **Findings CRITICAL/HIGH resolvidos:** 9/9. MEDIUM/LOW: 4/4.
- **Breaking changes de segurança:**
  - `POST /admin/query` removido.
  - Campo `senha` removido de `GET /usuarios` e `GET /usuarios/<id>`.
  - Campos `secret_key`, `debug` e `db_path` removidos de `GET /health`.
  - Exigem `Authorization: Bearer <token>`: de admin — `POST/PUT/DELETE /produtos`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db`; do próprio usuário ou admin — `GET /usuarios/<id>`, `POST /pedidos`, `GET /pedidos/usuario/<id>`.
  - CORS restrito a `CORS_ORIGINS` (padrão `http://localhost:3000`); servidor escuta em `127.0.0.1` por padrão; `DEBUG` desligado por padrão.
- **Outras mudanças de comportamento:**
  - `POST /login` devolve também `token`.
  - Toda resposta de erro tem a forma `{"erro": ..., "sucesso": false}`; erros 500 não expõem mais a mensagem interna.
  - `PUT /produtos/<id>` passa a aplicar a mesma validação do `POST` (tamanho do nome, categoria).
  - Entrada inválida que antes dava 500 agora dá 400 (filtro de preço não numérico, login sem body, tipos errados em produto/pedido); `quantidade` ≤ 0 em item de pedido é rejeitada.
