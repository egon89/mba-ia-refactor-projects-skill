# Draft — Seção "Análise Manual" (insumo para o README final)

## Projeto 1 — code-smells-project (Python/Flask)

1. **[CRITICAL] SQL Injection generalizada** — `models.py:28,47-50,57-61,68,92,109-111,126-129,140,148-151,154-166,174,188,192,220,224,279-281,289-297`. Praticamente toda query é montada por concatenação de string com dados vindos direto da requisição (ex.: `"SELECT * FROM produtos WHERE id = " + str(id)`, `login_usuario` concatenando email/senha no WHERE). Permite extração/alteração arbitrária de dados e, em `login_usuario`, bypass de autenticação via injeção clássica (`' OR '1'='1`).
2. **[CRITICAL] Endpoint `/admin/query` executa SQL arbitrário sem autenticação** — `app.py:59-78`. Recebe `sql` no corpo da requisição e executa via `cursor.execute(query)` sem qualquer verificação de identidade/permissão — controle total do banco para qualquer chamador externo.
3. **[CRITICAL] Credenciais/segredo hardcoded e reexposto** — `app.py:7` (`SECRET_KEY = "minha-chave-super-secreta-123"`), reexposto em `controllers.py:289` dentro da resposta JSON de `/health`.
4. **[HIGH] Senhas em texto plano** — seed em `database.py` grava senhas (`"admin123"`, `"123456"`) sem hash; `login_usuario` (`models.py:105-120`) compara senha em texto puro; `get_todos_usuarios`/`get_usuario_por_id` (`models.py:72-87`, `89-103`) retornam o campo `senha` crua nas respostas da API.
5. **[HIGH] DEBUG=True + CORS totalmente aberto em app que se declara "producao"** — `app.py:8-9` habilita o debugger do Werkzeug (RCE se exposto) e CORS irrestrito, enquanto `controllers.py:286` informa `"ambiente": "producao"`.
6. **[MEDIUM] N+1 queries em listagem de pedidos** — `get_pedidos_usuario` (`models.py:171-201`) e `get_todos_pedidos` (`models.py:203-233`) abrem um cursor por pedido e outro por item dentro do loop, em vez de um JOIN.
7. **[MEDIUM] Validação ausente/inconsistente** — `criar_pedido` (`controllers.py`) não valida quantidade negativa de itens; `buscar_produtos` (`models.py:285-297`) interpola `termo`/`categoria` direto na query sem sanitização.
8. **[LOW] Magic numbers** — limites de nome (`2`/`200`) espalhados em `controllers.py`; faixas de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) hardcoded em `relatorio_vendas` (`models.py:256-262`).
9. **[LOW] Tratamento de erro genérico que vaza detalhes internos** — `except Exception as e: return jsonify({"erro": str(e)})` repetido por todo `controllers.py`, expondo stack/mensagens internas ao cliente.

## Projeto 2 — ecommerce-api-legacy (Node.js/Express)

1. **[CRITICAL] Segredos/chave de pagamento hardcoded e logada em texto plano** — `src/utils.js:2-6` (`dbPass`, `paymentGatewayKey: "pk_live_..."`); a chave e o número do cartão são impressos juntos no console em `AppManager.js:45`.
2. **[CRITICAL] "Hash" de senha quebrado (`badCrypto`)** — `src/utils.js:17-23` apenas repete base64 do valor original 10.000 vezes e trunca para 10 caracteres: reversível (base64 não é hash) e sem salt. Usado para senha de novos usuários em `AppManager.js:68`.
3. **[CRITICAL/HIGH] God Class** — `AppManager.js` (141 linhas) concentra conexão/schema do banco, seed de dados e toda a lógica de checkout/relatório/exclusão de usuário, sem nenhuma camada de separação (viola MVC por completo).
4. **[HIGH] Validação de pagamento fictícia** — `AppManager.js:46`: `status = cc.startsWith("4") ? "PAID" : "DENIED"` — qualquer cartão começando com "4" é aprovado, sem integração real de gateway, e o número do cartão é aceito/logado em texto plano (risco de compliance PCI).
5. **[HIGH] Callback hell / tratamento de erro inconsistente** — `AppManager.js:37-77`, checkout com 5-6 níveis de callbacks aninhados; alguns `err` são silenciosamente ignorados (ex. `AppManager.js:57`).
6. **[MEDIUM] N+1 aninhado no relatório financeiro** — `AppManager.js:80-129`: loop de cursos → loop de matrículas → 2 queries por matrícula (usuário + pagamento), usando contadores manuais (`coursesPending`/`enrPending`) em vez de `Promise.all`.
7. **[MEDIUM] Integridade de dados comprometida deliberadamente** — `DELETE /api/users/:id` (`AppManager.js:131-137`) remove o usuário mas deixa `enrollments`/`payments` órfãos, e a própria mensagem de resposta admite isso.
8. **[LOW] Nomenclatura de variáveis ilegível** — variáveis de uma letra no fluxo de checkout (`u`, `e`, `p`, `cid`, `cc` em `AppManager.js:29-33`).
9. **[LOW] Uso de API legada/estilo deprecated** — `require('sqlite3').verbose()` com API 100% callback-based (`AppManager.js:1`), em vez de uma API baseada em Promises/async-await.

## Projeto 3 — task-manager-api (Python/Flask, parcialmente organizado)

1. **[CRITICAL] Hash de senha com MD5** — `models/user.py:27-32` (`set_password`/`check_password` usam `hashlib.md5`), algoritmo criptograficamente quebrado e sem salt — classifica-se também como uso de API/prática deprecated para senhas.
2. **[CRITICAL] Senha (hash) retornada pela API** — `models/user.py:16-25` (`to_dict` inclui `password`), exposta em `GET /users/<id>` e nas respostas de criação/atualização (`routes/user_routes.py` por volta das linhas 33, 85-86, 129).
3. **[HIGH] Autenticação fake / sem proteção real de rotas** — login retorna `'fake-jwt-token-' + str(user.id)` (`routes/user_routes.py:210`), token trivialmente forjável; nenhuma rota tem verificação de token/autorização.
4. **[HIGH] Lógica de negócio duplicada em 4 lugares (viola DRY/SRP)** — o cálculo de "tarefa atrasada" é recopiado em `models/task.py` (método `is_overdue`, correto), `routes/task_routes.py:30-39` e `:71-80`, e de novo em `routes/report_routes.py:33-43` e `:132-135`, em vez de reaproveitar o método do model.
5. **[MEDIUM] N+1 queries em listagens e relatórios** — `routes/task_routes.py:41-57` consulta `User`/`Category` por linha dentro do loop de tarefas; `routes/report_routes.py:53-68` refaz `Task.query.filter_by(user_id=...)` por usuário; `routes/report_routes.py:157-165` refaz contagem por categoria dentro do loop.
6. **[MEDIUM] Recurso mal posicionado** — rotas de `Category` (`/categories...`) vivem dentro de `report_routes.py:157-223`, sem relação com relatórios.
7. **[LOW] Código morto / inconsistência entre camadas** — `utils/helpers.py` define constantes de validação (`VALID_STATUSES`, `MAX_TITLE_LENGTH` etc.) e um validador `process_task_data()` que nunca são importados pelas rotas, que reimplementam a mesma validação inline (`routes/task_routes.py:96-100,110,113-114`); o `NotificationService` existe mas nunca é chamado por nenhuma rota.
8. **[LOW] "Boolean madness" / estilo de código** — `models/user.py:34-38` (`is_admin`) e `models/task.py` usam `if cond: return True else: return False` em vez de `return cond`.

---

**Resumo por severidade (preliminar):**
| Projeto | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|
| code-smells-project | 3 | 2 | 2 | 2 |
| ecommerce-api-legacy | 2 | 2 (+1 compartilhado) | 2 | 2 |
| task-manager-api | 2 | 2 | 2 | 2 |

Todos os 3 projetos atendem ao mínimo exigido (≥5 problemas, ≥1 CRITICAL/HIGH, ≥2 MEDIUM, ≥2 LOW).
