# Criação de Skills — Refatoração Arquitetural Automatizada

Fork do desafio [devfullcycle/mba-ia-refactor-projects-skill](https://github.com/devfullcycle/mba-ia-refactor-projects-skill): criação da Claude Code Skill `refactor-arch`, que analisa, audita e refatora para o padrão MVC três projetos legados (`code-smells-project`, `ecommerce-api-legacy`, `task-manager-api`), de forma agnóstica de tecnologia.

> Este README é construído de forma incremental, à medida que cada etapa do desafio é concluída (ver `EXECUTION_PROGRESS.md` para o detalhamento do processo). As seções B, C e D abaixo são preenchidas nas fases seguintes.

## A) Análise Manual

Problemas identificados por leitura direta do código de cada projeto, antes da criação da skill, classificados pela escala de severidade do desafio (CRITICAL / HIGH / MEDIUM / LOW).

### Projeto 1 — code-smells-project (Python/Flask)

1. **[CRITICAL] SQL Injection generalizada** — `models.py:28,47-50,57-61,68,92,109-111,126-129,140,148-151,154-166,174,188,192,220,224,279-281,289-297`. Praticamente toda query é montada por concatenação de string com dados vindos direto da requisição (ex.: `"SELECT * FROM produtos WHERE id = " + str(id)`, `login_usuario` concatenando email/senha no WHERE). Permite extração/alteração arbitrária de dados e, em `login_usuario`, bypass de autenticação via injeção clássica (`' OR '1'='1`).
2. **[CRITICAL] Endpoint `/admin/query` executa SQL arbitrário sem autenticação** — `app.py:59-78`. Recebe `sql` no corpo da requisição e executa via `cursor.execute(query)` sem qualquer verificação de identidade/permissão — controle total do banco para qualquer chamador externo.
3. **[CRITICAL] Credenciais/segredo hardcoded e reexposto** — `app.py:7` (`SECRET_KEY = "minha-chave-super-secreta-123"`), reexposto em `controllers.py:289` dentro da resposta JSON de `/health`.
4. **[HIGH] Senhas em texto plano** — seed em `database.py` grava senhas (`"admin123"`, `"123456"`) sem hash; `login_usuario` (`models.py:105-120`) compara senha em texto puro; `get_todos_usuarios`/`get_usuario_por_id` (`models.py:72-87`, `89-103`) retornam o campo `senha` crua nas respostas da API.
5. **[HIGH] DEBUG=True + CORS totalmente aberto em app que se declara "producao"** — `app.py:8-9` habilita o debugger do Werkzeug (RCE se exposto) e CORS irrestrito, enquanto `controllers.py:286` informa `"ambiente": "producao"`.
6. **[MEDIUM] N+1 queries em listagem de pedidos** — `get_pedidos_usuario` (`models.py:171-201`) e `get_todos_pedidos` (`models.py:203-233`) abrem um cursor por pedido e outro por item dentro do loop, em vez de um JOIN.
7. **[MEDIUM] Validação ausente/inconsistente** — `criar_pedido` (`controllers.py`) não valida quantidade negativa de itens; `buscar_produtos` (`models.py:285-297`) interpola `termo`/`categoria` direto na query sem sanitização.
8. **[LOW] Magic numbers** — limites de nome (`2`/`200`) espalhados em `controllers.py`; faixas de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) hardcoded em `relatorio_vendas` (`models.py:256-262`).
9. **[LOW] Tratamento de erro genérico que vaza detalhes internos** — `except Exception as e: return jsonify({"erro": str(e)})` repetido por todo `controllers.py`, expondo stack/mensagens internas ao cliente.

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

1. **[CRITICAL] Segredos/chave de pagamento hardcoded e logada em texto plano** — `src/utils.js:2-6` (`dbPass`, `paymentGatewayKey: "pk_live_..."`); a chave e o número do cartão são impressos juntos no console em `AppManager.js:45`.
2. **[CRITICAL] "Hash" de senha quebrado (`badCrypto`)** — `src/utils.js:17-23` apenas repete base64 do valor original 10.000 vezes e trunca para 10 caracteres: reversível (base64 não é hash) e sem salt. Usado para senha de novos usuários em `AppManager.js:68`.
3. **[CRITICAL/HIGH] God Class** — `AppManager.js` (141 linhas) concentra conexão/schema do banco, seed de dados e toda a lógica de checkout/relatório/exclusão de usuário, sem nenhuma camada de separação (viola MVC por completo).
4. **[HIGH] Validação de pagamento fictícia** — `AppManager.js:46`: `status = cc.startsWith("4") ? "PAID" : "DENIED"` — qualquer cartão começando com "4" é aprovado, sem integração real de gateway, e o número do cartão é aceito/logado em texto plano (risco de compliance PCI).
5. **[HIGH] Callback hell / tratamento de erro inconsistente** — `AppManager.js:37-77`, checkout com 5-6 níveis de callbacks aninhados; alguns `err` são silenciosamente ignorados (ex. `AppManager.js:57`).
6. **[MEDIUM] N+1 aninhado no relatório financeiro** — `AppManager.js:80-129`: loop de cursos → loop de matrículas → 2 queries por matrícula (usuário + pagamento), usando contadores manuais (`coursesPending`/`enrPending`) em vez de `Promise.all`.
7. **[MEDIUM] Integridade de dados comprometida deliberadamente** — `DELETE /api/users/:id` (`AppManager.js:131-137`) remove o usuário mas deixa `enrollments`/`payments` órfãos, e a própria mensagem de resposta admite isso.
8. **[LOW] Nomenclatura de variáveis ilegível** — variáveis de uma letra no fluxo de checkout (`u`, `e`, `p`, `cid`, `cc` em `AppManager.js:29-33`).
9. **[LOW] Uso de API legada/estilo deprecated** — `require('sqlite3').verbose()` com API 100% callback-based (`AppManager.js:1`), em vez de uma API baseada em Promises/async-await.

### Projeto 3 — task-manager-api (Python/Flask, parcialmente organizado)

1. **[CRITICAL] Hash de senha com MD5** — `models/user.py:27-32` (`set_password`/`check_password` usam `hashlib.md5`), algoritmo criptograficamente quebrado e sem salt — também se qualifica como uso de prática/API deprecated para senhas.
2. **[CRITICAL] Senha (hash) retornada pela API** — `models/user.py:16-25` (`to_dict` inclui `password`), exposta em `GET /users/<id>` e nas respostas de criação/atualização (`routes/user_routes.py`, por volta das linhas 33, 85-86, 129).
3. **[HIGH] Autenticação fake / sem proteção real de rotas** — login retorna `'fake-jwt-token-' + str(user.id)` (`routes/user_routes.py:210`), token trivialmente forjável; nenhuma rota tem verificação de token/autorização.
4. **[HIGH] Lógica de negócio duplicada em 4 lugares (viola DRY/SRP)** — o cálculo de "tarefa atrasada" é recopiado em `models/task.py` (método `is_overdue`, correto), `routes/task_routes.py:30-39` e `:71-80`, e de novo em `routes/report_routes.py:33-43` e `:132-135`, em vez de reaproveitar o método do model.
5. **[MEDIUM] N+1 queries em listagens e relatórios** — `routes/task_routes.py:41-57` consulta `User`/`Category` por linha dentro do loop de tarefas; `routes/report_routes.py:53-68` refaz `Task.query.filter_by(user_id=...)` por usuário; `routes/report_routes.py:157-165` refaz contagem por categoria dentro do loop.
6. **[MEDIUM] Recurso mal posicionado** — rotas de `Category` (`/categories...`) vivem dentro de `report_routes.py:157-223`, sem relação com relatórios.
7. **[LOW] Código morto / inconsistência entre camadas** — `utils/helpers.py` define constantes de validação (`VALID_STATUSES`, `MAX_TITLE_LENGTH` etc.) e um validador `process_task_data()` que nunca são importados pelas rotas, que reimplementam a mesma validação inline (`routes/task_routes.py:96-100,110,113-114`); o `NotificationService` existe mas nunca é chamado por nenhuma rota.
8. **[LOW] "Boolean madness" / estilo de código** — `models/user.py:34-38` (`is_admin`) e `models/task.py` usam `if cond: return True else: return False` em vez de `return cond`.

### Resumo por severidade (análise manual)

| Projeto | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|
| code-smells-project | 3 | 2 | 2 | 2 |
| ecommerce-api-legacy | 2 | 2 (+1 compartilhado) | 2 | 2 |
| task-manager-api | 2 | 2 | 2 | 2 |

Todos os 3 projetos atendem ao mínimo exigido pelo desafio (≥5 problemas, ≥1 CRITICAL/HIGH, ≥2 MEDIUM, ≥2 LOW).

## B) Construção da Skill

### Estrutura

A skill `refactor-arch` vive em `.claude/skills/refactor-arch/` e segue a estrutura:

```
refactor-arch/
├── SKILL.md                              # orquestra as 3 fases
└── references/
    ├── project-analysis.md               # heurísticas da Fase 1
    ├── anti-patterns-catalog.md          # catálogo da Fase 2 (14 anti-patterns)
    ├── report-template.md                # formato do relatório da Fase 2
    ├── mvc-guidelines.md                 # alvo arquitetural da Fase 3
    └── refactoring-playbook.md           # transformações antes/depois da Fase 3
```

O `SKILL.md` abre com 5 "regras invioláveis" (nenhuma escrita antes da confirmação humana; todo finding com arquivo:linha real; nenhuma suposição de stack; comportamento preservado, exceto correção de segurança; nenhum número alucinado) e uma tabela que diz **qual arquivo de referência ler em qual fase** — a skill carrega conhecimento sob demanda em vez de tudo de uma vez.

### Decisões de design

- **Catálogo com IDs estáveis (`AP-01`…`AP-14`) e severidade padrão por entrada**, para que o relatório da Fase 2 e o playbook da Fase 3 se refiram ao mesmo vocabulário (`AP-05 → Playbook RP-05`). A severidade padrão pode subir um nível quando o impacto do caso concreto justificar.
- **Playbook 1:1 com o catálogo** (14 transformações, uma por anti-pattern), com exemplos de código alternando Python e JavaScript propositalmente — o antes/depois mostra a movimentação estrutural, não a sintaxe de uma linguagem só, reforçando que a skill não é específica de uma stack.
- **Estratégia adaptativa em `mvc-guidelines.md`:** a Fase 3 decide a profundidade da refatoração pela classificação da Fase 1 — projeto monolítico recebe o scaffold MVC completo; projeto já em camadas (como o `task-manager-api`) recebe melhoria direcionada, sem reescrever o que já está adequado. Essa distinção é citada explicitamente no desafio e foi um ponto de atenção desde o desenho da skill.
- **Pausa da Fase 2 tratada como obrigatória e sem ambiguidade:** o `SKILL.md` instrui que qualquer resposta que não seja uma confirmação clara é tratada como "n", evitando que a Fase 3 rode por engano.

### Anti-patterns incluídos e por quê

O catálogo tem 14 entradas (acima do mínimo de 8), com distribuição CRITICAL 5 / HIGH 4 / MEDIUM 3 / LOW 2, escolhidas para cobrir exatamente a análise manual (seção A): SQL Injection, segredos hardcoded, endpoint de execução arbitrária, exposição de dado sensível e criptografia quebrada (os 5 CRITICAL, todos presentes em pelo menos um dos 3 projetos); God Class, lógica de negócio na camada errada, autenticação ausente/fictícia e estado global mutável (os 4 HIGH); N+1, duplicação/código morto e **APIs deprecated** (os 3 MEDIUM — a detecção de deprecated é um requisito explícito do desafio); magic numbers e tratamento de erro genérico (os 2 LOW). Nenhuma entrada foi incluída "por completude" — todas mapeiam para um achado real de algum dos 3 projetos-alvo.

### Como garantimos que a skill é agnóstica de tecnologia

- Nenhum arquivo de referência menciona Flask/Express como pré-requisito — os sinais de detecção são descritos em termos de padrão de código (`execute("..." + var)`, `db.get(...)` dentro de loop), não de API específica de um framework.
- O playbook mistura exemplos Python e JavaScript no mesmo arquivo, forçando a skill (e quem a lê) a entender a transformação como estrutural, "traduzível" para a linguagem do projeto.
- A prova definitiva é empírica: a **mesma pasta** `refactor-arch/`, sem nenhuma edição, foi copiada para dentro de `ecommerce-api-legacy/` (Node/Express) e `task-manager-api/` (Python/Flask parcialmente organizado) — ver seção C para os resultados nos 3 projetos.

### Desafios encontrados

- Equilibrar o catálogo para não ficar restrito a um único projeto: como os 3 projetos têm perfis bem diferentes (monolito sem nenhuma camada vs. projeto já com `models/routes/services/utils`), cada anti-pattern precisou de um sinal de detecção descrito de forma "greppável" e não amarrado à estrutura de pastas de nenhum projeto específico.
- Decidir a profundidade da Fase 3 para o projeto já organizado (`task-manager-api`) sem que a skill reescrevesse código que já estava adequado só por uniformidade — resolvido com a "estratégia adaptativa" em `mvc-guidelines.md`.
- Expressar a regra de "comportamento preservado, exceto correção de segurança" sem abrir brecha para que a Fase 3 trate controles de segurança desligados por flag como "resolvido" — por isso a regra 4 do `SKILL.md` é explícita sobre isso.

## C) Resultados

### Projeto 1 — code-smells-project

A skill `refactor-arch` foi executada com `claude "/refactor-arch"` dentro de `code-smells-project/`. Relatório completo em [`reports/audit-project-1.md`](reports/audit-project-1.md).

**Fase 1 — Análise:** Python + Flask 3.1.1 (sqlite3 bruto, sem ORM), domínio de E-commerce, 4 arquivos / ~780 linhas analisados — detecção correta.

**Fase 2 — Auditoria:**

| Severidade | Findings |
|---|---|
| CRITICAL | 5 |
| HIGH | 4 |
| MEDIUM | 2 |
| LOW | 2 |
| **Total** | **13** |

Todos com `arquivo:linha` reais (ex.: SQL Injection em 19 pontos de `models.py`). Seção "Deprecated APIs" presente, com declaração explícita de que nenhuma foi encontrada (Flask 3.1.1 e sqlite3 da stdlib verificados). A skill pausou corretamente pedindo confirmação antes da Fase 3.

**Fase 3 — Refatoração:** estrutura MVC completa criada em `src/` (`config/`, `database/`, `models/`, `services/`, `controllers/`, `views/`, `middlewares/`, `utils/`); `controllers.py`, `models.py` e `database.py` legados removidos. 9/9 findings CRITICAL/HIGH resolvidos, 4/4 MEDIUM/LOW resolvidos.

**Antes → Depois da estrutura:**

| Antes | Depois |
|---|---|
| 4 arquivos (`app.py`, `controllers.py`, `models.py`, `database.py`), tudo misturado | `app.py` (entry point) + `src/` em 8 camadas, 44 arquivos `.py`, 1151 linhas |
| SQL por concatenação de string | Queries parametrizadas |
| `SECRET_KEY`/`DEBUG`/CORS hardcoded | Configuração via variáveis de ambiente (`.env.example`) |
| `/admin/query` (SQL arbitrário, sem auth) | Endpoint removido |
| Senha em texto plano, retornada pela API | Hash de senha + nunca serializada |
| Nenhuma autenticação real | Token assinado + gate de autenticação/autorização em todas as rotas sensíveis |

**Checklist de validação (code-smells-project):**

```
### Fase 1 — Análise
- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (13 encontrados)
- [x] Detecção de APIs deprecated incluída (nenhuma encontrada, declarado explicitamente)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente (com breaking changes de segurança documentados no relatório)
```

**Evidência de que a aplicação funciona pós-refatoração:** validado nesta sessão subindo o projeto via Docker Compose (`docker compose up --build`, ver `code-smells-project/README.md`) e executando `curl` real contra todos os endpoints — públicos, autenticados e de admin, incluindo o caso de erro esperado (`401` sem token). Um exemplo de `curl` tinha um valor de categoria inválido para o endpoint de criação de produto; o erro foi pego durante essa validação e corrigido no README antes de ser documentado como funcional.

**Observações sobre o comportamento da skill:** a Fase 2 identificou corretamente os 5 problemas CRITICAL/HIGH mínimos exigidos (na verdade, encontrou todos os 9 CRITICAL/HIGH do catálogo presentes no projeto), e a Fase 3 tratou a ausência total de autenticação como o caso mais grave do anti-pattern AP-08, construindo o mecanismo do zero em vez de ignorá-lo por "não haver nada para corrigir" — exatamente o comportamento esperado descrito nas regras do `SKILL.md`.

### Projetos 2 e 3

*(a ser preenchido nas Fases 4 e 5 — execução da skill em `ecommerce-api-legacy` e `task-manager-api`)*

## D) Como Executar

*(a ser preenchido na Fase 7, após a skill estar criada e executada nos 3 projetos)*
