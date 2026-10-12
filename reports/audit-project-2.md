# Audit — ecommerce-api-legacy

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4
Files:   3 analisados | ~180 linhas de código

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 4 | LOW: 1

## Findings

### [CRITICAL] Segredos hardcoded (AP-02)
File: src/utils.js:2-5
Description: Credenciais literais no código versionado: dbUser (:2), dbPass "senha_super_secreta_prod_123" (:3), paymentGatewayKey "pk_live_..." (:4), smtpUser (:5).
Impact: Qualquer pessoa com acesso ao repositório ou ao histórico tem a senha de produção e a chave live do gateway.
Recommendation: RP-01 — mover para variáveis de ambiente em config/, sem default para segredos; rotacionar as chaves já expostas.

### [CRITICAL] Dado de pagamento e segredo em log (AP-04)
File: src/AppManager.js:45
Description: console.log imprime o número completo do cartão (cc) e a paymentGatewayKey a cada checkout.
Impact: PAN em texto plano nos logs (violação de PCI-DSS) e a chave do gateway reexposta em todo agregador de log.
Recommendation: RP-04 — remover o log; se precisar de rastreio, logar só os 4 últimos dígitos e nunca a chave.

### [CRITICAL] Hashing de senha quebrado (AP-05)
File: src/utils.js:17-23
Description: badCrypto concatena 10.000 vezes os 2 primeiros caracteres do base64 da senha e corta em 10 caracteres. O "hash" depende só dos primeiros 12 bits da senha, sem salt.
  - src/AppManager.js:68 — uso no checkout, com senha default "123456" quando pwd não é enviado
  - src/AppManager.js:18 — seed grava a senha '123' em texto plano
Impact: Senhas diferentes com o mesmo início geram o mesmo hash, e o valor é trivialmente reversível. Contas são criadas com senha conhecida.
Recommendation: RP-05 — hash dedicado com salt (crypto.scrypt nativo ou bcrypt); remover o default "123456"; aplicar o hash no seed.

### [HIGH] God Class (AP-06)
File: src/AppManager.js:4-139
Description: AppManager abre a conexão (:7), cria schema e seed (:10-23), registra rotas (:25-138) e implementa checkout, relatório e remoção de usuário.
Impact: Zero separação MVC; nada é testável em isolamento; qualquer mudança toca o arquivo inteiro.
Recommendation: RP-06 — dividir em config/, models/, services/, controllers/, routes/ e middlewares/, com injeção da conexão.

### [HIGH] Lógica de negócio na camada de rota, sem transação (AP-07)
File: src/AppManager.js:28-78
Description: O handler HTTP decide o pagamento e orquestra 4 escritas encadeadas sem transação.
  - :46 — regra de aprovação do pagamento (cartão começa com "4") dentro da rota
  - :69 antes de :48 — o usuário é criado antes da decisão; pagamento recusado deixa usuário órfão
  - :50, :54 — matrícula gravada antes do pagamento; falha em :54 deixa matrícula sem pagamento
  - :108-110 — cálculo de receita do relatório dentro da rota
  - :133-135 — DELETE remove só o usuário; matrículas e pagamentos ficam órfãos (a própria resposta admite)
Impact: Regra não reutilizável nem testável; estado inconsistente no banco em qualquer falha parcial.
Recommendation: RP-07 — extrair CheckoutService, PaymentService e ReportService; envolver o checkout e a remoção em transação.

### [HIGH] Autenticação e autorização ausentes (AP-08)
File: src/AppManager.js:80, src/AppManager.js:131
Description: Nenhuma rota exige credencial.
  - :80 — /api/admin/financial-report (receita e nomes de alunos) é público
  - :131 — DELETE /api/users/:id é público
  - :40, :74 — checkout com e-mail já cadastrado matricula o usuário existente sem verificar a senha
Impact: Qualquer chamador lê o relatório financeiro e apaga qualquer usuário.
Recommendation: RP-08 — middleware de autenticação nas rotas admin e de remoção (breaking change de segurança).

### [HIGH] Erros ignorados derrubam o processo ou mascaram falha (AP-14, severidade elevada)
File: src/AppManager.js:46, :57, :92, :104, :106, :133
Description: Não há tratamento de erro centralizado e vários callbacks descartam err.
  - :46 — cc.startsWith é chamado sem checar o tipo; "card" numérico no JSON passa pela validação de :35 e lança TypeError dentro do callback do banco
  - :92 — err ignorado; em falha, enrollments é undefined e :93 lança TypeError
  - :57, :104, :106 — err ignorado silenciosamente
  - :133 — err ignorado; o DELETE responde 200 mesmo se falhar ou se o id não existir
Impact: Uma única requisição não autenticada com "card": 4111 encerra o servidor por exceção não capturada (confirmado na linha de base da Fase 3). Elevado de LOW para HIGH por isso.
Recommendation: RP-14 — validação de entrada com tipos, async/await com try/catch e error handler central do Express.

### [MEDIUM] Estado global mutável (AP-09, severidade reduzida)
File: src/utils.js:9-15
Description: globalCache (:9) é um objeto de módulo mutado por logAndCache (:14, chamado em AppManager.js:59) e nunca lido nem expirado.
Impact: Cresce uma chave por usuário sem limite e é compartilhado entre requisições. Reduzido de HIGH porque hoje ninguém lê o cache, então não há corrida observável.
Recommendation: RP-09 — remover o cache; se for necessário, encapsular em um serviço injetado com limite e TTL.

### [MEDIUM] Queries N+1 (AP-10)
File: src/AppManager.js:89-126
Description: O relatório faz 1 query de cursos (:83), 1 de matrículas por curso (:92) e 2 por matrícula (:104 usuário, :106 pagamento), coordenadas por contadores manuais (:86, :93).
Impact: 1 + C + 2E round-trips por requisição; a ordem do resultado depende da ordem de retorno dos callbacks.
Recommendation: RP-10 — uma query com JOIN courses/enrollments/users/payments, agregada no model.

### [MEDIUM] Código morto (AP-11)
File: src/utils.js:10, src/utils.js:25, src/AppManager.js:2
Description: totalRevenue é declarado (utils.js:10), exportado (:25) e importado (AppManager.js:2) sem nunca ser usado. globalCache é exportado e nunca importado. config.dbUser, dbPass e smtpUser (utils.js:2,3,5) não são lidos em lugar nenhum.
Impact: Confunde a leitura e mantém segredos sem função no código.
Recommendation: RP-11 — remover.

### [MEDIUM] API de banco 100% callback (AP-12)
File: src/AppManager.js:37-77, src/AppManager.js:83-128
Description: Ver seção Deprecated APIs.
Impact: Até 5 níveis de callback aninhado, origem direta dos erros ignorados acima.
Recommendation: RP-12 — camada promisificada + async/await.

### [LOW] Nomenclatura ruim e magic values (AP-13)
File: src/AppManager.js:29-33, :46, :68; src/utils.js:19
Description: Variáveis u, e, p, cid, cc (:29-33) num fluxo de pagamento; literais sem nome "4" (:46), "123456" (:68), 10000 (utils.js:19); a classe se chama AppManager e a função, badCrypto.
Impact: Intenção implícita; mudar uma regra exige caçar o literal.
Recommendation: RP-13 — nomes de domínio e constantes. Os campos do body (usr, eml, pwd, c_id, card) são contrato e ficam como estão.

## Deprecated APIs
- src/AppManager.js:37, :40, :50, :54, :57, :69, :83, :92, :104, :106, :133 — sqlite3 em estilo callback (db.get/db.run/db.all). O pacote sqlite3 5.x não expõe Promises nativamente; o equivalente moderno é um wrapper promisificado (util.promisify ou helper próprio em config/database) consumido com async/await.
- Express 4.18: nenhuma API removida ou deprecated em uso (express.json() é a forma atual).

Checados e ausentes: AP-01 (todas as 11 queries com input usam placeholders "?") e AP-03 (nenhum endpoint de SQL/comando livre).

================================
Total: 12 findings
================================
```

Os caminhos e linhas acima se referem ao código anterior à refatoração (`src/AppManager.js` e `src/utils.js` foram removidos).

## Resultado da Refatoração

- **Estrutura MVC criada:** `src/app.js` (composition root, `createApp`) + `config/` (env e regras de negócio nomeadas), `database/` (conexão com Promises e transação, schema/seed), `models/` (user, course, enrollment, payment, auditLog), `services/` (checkout, payment, report, user, password), `controllers/` (checkout, report, user), `routes/` (checkout, admin, user), `middlewares/` (auth, errorHandler), `utils/` (errors, asyncHandler). 25 arquivos `.js`, 534 linhas. `src/AppManager.js` e `src/utils.js` foram removidos. Nenhuma dependência nova (hash de senha usa `crypto.scrypt` nativo).
- **Validação:**
  - Boot com `node src/app.js` sem erro no log.
  - 15 chamadas da linha de base repetidas com token de admin: 6 idênticas (checkout ok, recusado, usuário existente, campos faltando, curso inexistente, 404 de rota). As 9 diferentes são todas esperadas: 3 relatórios (ordem agora determinística por id do curso; sem órfãos após o delete), 2 deletes (texto novo), checkout sem `pwd` (200 → 400), JSON inválido (página HTML com stack trace → `Bad Request`), `card` numérico (processo morto → 400) e a chamada seguinte a ele (sem resposta → 404 normal, servidor segue de pé).
  - Autenticação: sem token, token errado e `ADMIN_API_TOKEN` não configurado respondem 401 nas duas rotas protegidas.
  - 20 checkouts simultâneos com o mesmo e-mail novo: 20 respostas 200, 1 único usuário criado, 20 matrículas, 20 pagamentos, 20 audit logs.
  - Pagamento recusado para e-mail novo não cria usuário.
  - Senhas gravadas no formato `scrypt$salt$hash`, inclusive a do seed.
  - Sinais de detecção reexecutados: nenhum `console.log` além da mensagem de boot, nenhum segredo literal, nenhum SQL fora de `models/` e `database/`, nenhuma interpolação em SQL, nenhum resíduo de `badCrypto`/`globalCache`/`totalRevenue`.
- **Findings CRITICAL/HIGH resolvidos:** 7/7. MEDIUM/LOW: 5/5.
- **Breaking changes de segurança:**
  - `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem `Authorization: Bearer <ADMIN_API_TOKEN>`; sem a variável definida, respondem sempre 401.
  - `POST /api/checkout` para e-mail novo sem `pwd` responde 400 (antes criava a conta com a senha "123456").
  - `POST /api/checkout` com `usr`, `eml` ou `card` que não sejam string responde 400.
- **Outras mudanças de comportamento:**
  - `DELETE /api/users/:id` apaga também matrículas e pagamentos do usuário, em transação; a receita desses pagamentos sai do relatório. O texto de sucesso passou a ser "Usuário deletado junto com suas matrículas e pagamentos.". Continua respondendo 200 para id inexistente.
  - Pagamento recusado não deixa mais usuário criado.
  - Relatório financeiro vem ordenado por id do curso e da matrícula.
  - Erros 500 respondem "Erro interno. Tente novamente." em vez de "Erro DB" / "Erro Matrícula" / "Erro Pagamento" / "Erro ao criar usuário".
