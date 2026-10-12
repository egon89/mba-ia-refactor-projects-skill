# Execution Progress — Desafio refactor-arch

Última atualização: 2026-10-10
Repositório: egon89/mba-ia-refactor-projects-skill (fork de devfullcycle/mba-ia-refactor-projects-skill)

## Legenda de status
⬜ Pendente · 🔄 Em andamento · ✅ Concluída · ⛔ Bloqueada (aguardando ação humana)

## Resumo rápido (dashboard)

| Fase | Etapas | Status | Ação humana pendente? |
|---|---|---|---|
| 0. Setup | 0.1–0.2 | ✅ | Não |
| 1. Análise manual | 1.1–1.4 | ✅ | Não |
| 2. Criação da skill | 2.1–2.6 | 🔄 | Sim — 2.6 (aprovar commit) |
| 3. Execução Projeto 1 (code-smells-project) | 3.1–3.6 | ✅ | Não |
| 4. Execução Projeto 2 (ecommerce-api-legacy) | 4.1–4.6 | ⬜ | Sim — 4.2/4.4/4.5/4.6 |
| 5. Execução Projeto 3 (task-manager-api) | 5.1–5.6 | ⬜ | Sim — 5.2/5.4/5.5/5.6 |
| 6. Relatórios e evidências | 6.1–6.3 | ⬜ | Sim — 6.3 (capturar evidências) |
| 7. README final | 7.1–7.4 | ⬜ | Sim — revisão de conteúdo |
| 8. Entrega | 8.1–8.3 | ⬜ | Sim — push final + verificação pública |

## Pontos de ação humana obrigatória (não delegáveis)

1. **3.3 / 4.4 / 5.4** — as 3 pausas de confirmação da Fase 2 de cada execução da skill (requisito explícito do desafio: "A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo").
2. **3.1/3.4, 4.2/4.5, 5.2/5.5** — execução interativa do comando `claude "/refactor-arch"` e validação manual de boot/endpoints pós-refatoração.
3. **1.4** — aprovação do conteúdo da análise manual antes de seguir para a criação da skill.
4. **6.3** — captura de evidências (screenshots/logs das apps rodando).
5. **7.1–7.4** — revisão do README final antes de publicar.
6. **8.2 / 8.3** — autorização explícita do push final e verificação pública do repositório.

## Regra sobre atualização incremental do README.md

O `README.md` final **não é escrito de uma vez só na Fase 7** — ele é atualizado gradualmente, ao final de cada etapa marcada abaixo com 📝, substituindo o texto do desafio por conteúdo real já naquele momento. A Fase 7 passa a ser só uma revisão/polimento final, não a primeira redação. Etapas que disparam atualização do README:
- **1.4** → cria a seção A) Análise Manual (substitui o texto do desafio pela primeira vez).
- **2.6** → preenche a seção B) Construção da Skill (decisões de design, catálogo, agnosticismo).
- **3.6 / 4.6 / 5.6** → acrescenta à seção C) Resultados os achados/checklist/comparação antes-depois de cada projeto, um por vez.
- **6.3** → incorpora evidências (logs/screenshots) na seção C.
- **7.1–7.4** → revisão final de consistência/tom de tudo que já foi incrementalmente escrito (não redação do zero).

---

## Fase 0 — Setup

### Etapa 0.1 — Confirmar fork no GitHub
- **Status:** ✅ Concluída
- **Fase do desafio:** Setup
- **Ação humana obrigatória:** Sim — confirmado pelo usuário em 2026-10-10.
- **Depende de:** —
- **Critério de "feito":** Remote `origin` aponta para `git@github.com:egon89/mba-ia-refactor-projects-skill.git`, branch `main` sincronizada, working tree limpo, usuário confirmou que é fork público válido.
- **Notas / decisões:** Confirmado — fork já existia antes do início deste plano. Nenhuma ação adicional necessária.

### Etapa 0.2 — Estratégia de commits
- **Status:** ✅ Concluída
- **Fase do desafio:** Setup
- **Ação humana obrigatória:** Sim — decisão do usuário.
- **Depende de:** 0.1
- **Critério de "feito":** Estratégia registrada.
- **Notas / decisões:** Um commit por marco relevante (ex.: "feat: add refactor-arch skill", "refactor: apply MVC to code-smells-project"). Sempre pedir aprovação explícita antes de `git commit`/`git push`. Nunca usar `--amend` ou force-push.

---

## Fase 1 — Análise manual dos 3 projetos

### Etapa 1.1 — Análise manual: code-smells-project
- **Status:** ✅ Concluída
- **Fase do desafio:** Análise manual
- **Depende de:** 0.1
- **Critério de "feito":** confirmação do usuário.
- **Notas / decisões:** Ver `ANALISE_MANUAL_DRAFT.md`.

### Etapa 1.2 — Análise manual: ecommerce-api-legacy
- **Status:** ✅ Concluída
- **Fase do desafio:** Análise manual
- **Depende de:** 0.1
- **Critério de "feito":** confirmação do usuário.
- **Notas / decisões:** Ver `ANALISE_MANUAL_DRAFT.md`.

### Etapa 1.3 — Análise manual: task-manager-api
- **Status:** ✅ Concluída
- **Fase do desafio:** Análise manual
- **Depende de:** 0.1
- **Critério de "feito":** confirmação do usuário.
- **Notas / decisões:** Ver `ANALISE_MANUAL_DRAFT.md`.

### Etapa 1.4 📝 — Consolidar e publicar a seção "Análise Manual" no README.md
- **Status:** ✅ Concluída
- **Fase do desafio:** Análise manual
- **Ação humana obrigatória:** Sim — revisar e aprovar o conteúdo antes de avançar para a Fase 2.
- **Depende de:** 1.1, 1.2, 1.3
- **Critério de "feito":** Após aprovação, o `README.md` do repo é atualizado substituindo o texto do desafio pela seção A) Análise Manual real (não fica mais só em `ANALISE_MANUAL_DRAFT.md`).
- **Notas / decisões:** Aprovado pelo usuário em 2026-10-10. `README.md` atualizado com a seção A) completa e placeholders para B/C/D. `ANALISE_MANUAL_DRAFT.md` pode ser removido num commit futuro (conteúdo já está no README) ou mantido como histórico — decidir ao commitar.

---

## Fase 2 — Design e criação da skill `refactor-arch`

### Etapa 2.1 — Definir estrutura de arquivos de referência
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 1.4
- **Critério de "feito":** Lista de arquivos decidida (SKILL.md + arquivos cobrindo as 5 áreas obrigatórias), combinando ideias de múltiplas referências em `resources/`.
- **Notas / decisões:** Estrutura: `SKILL.md` + `references/{project-analysis,anti-patterns-catalog,mvc-guidelines,refactoring-playbook,report-template}.md`. Inspirada (sem copiar literalmente) em 5 das 7 soluções de `resources/` (dayvisonassis, filipe1309, leomhl, javielrezende, glaide): catálogo com IDs estáveis (AP-NN) + tabela de severidade, playbook com antes/depois alternando Python/JS, SKILL.md com "regras invioláveis" + tabela de arquivos de referência carregados sob demanda.

### Etapa 2.2 — Escrever catálogo de anti-patterns
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não (recomendável revisão)
- **Depende de:** 2.1
- **Critério de "feito":** ≥8 anti-patterns, severidades distribuídas (CRITICAL/HIGH/MEDIUM/LOW), sinais de detecção concretos, detecção de APIs deprecated incluída, cobre os problemas reais da Fase 1.
- **Notas / decisões:** 14 anti-patterns (AP-01 a AP-14): CRITICAL 5 / HIGH 4 / MEDIUM 3 / LOW 2. AP-12 cobre detecção de APIs deprecated explicitamente. Catálogo cobre todos os achados da análise manual dos 3 projetos.

### Etapa 2.3 — Escrever demais arquivos de referência
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 2.1, 2.2
- **Critério de "feito":** `project-analysis.md`, `mvc-guidelines.md`, `refactoring-playbook.md` (≥8 transformações antes/depois), `report-template.md` escritos e consistentes entre si.
- **Notas / decisões:** Playbook com 14 transformações (RP-01 a RP-14), uma por anti-pattern do catálogo. `mvc-guidelines.md` inclui estratégia adaptativa (monolítico vs. já em camadas) — importante para o projeto 3. `report-template.md` segue o formato do exemplo do `challenge.md`, com seção obrigatória "Deprecated APIs".

### Etapa 2.4 — Escrever SKILL.md (3 fases)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 2.2, 2.3
- **Critério de "feito":** Orquestra Fase 1/2/3, com instrução inequívoca de pausa obrigatória na Fase 2 antes de qualquer modificação.
- **Notas / decisões:** 5 "regras invioláveis" no topo (nenhuma escrita antes do `y`, arquivo:linha real, nenhuma suposição de stack, comportamento preservado exceto correção de segurança, sem números alucinados). Pausa da Fase 2 é um `[y/n]` explícito com tratamento de resposta ambígua como "n".

### Etapa 2.5 — Posicionar a skill em code-smells-project
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 2.4
- **Critério de "feito":** `code-smells-project/.claude/skills/refactor-arch/SKILL.md` + arquivos de referência existem.
- **Notas / decisões:** Criada em `code-smells-project/.claude/skills/refactor-arch/` (SKILL.md + 5 arquivos em `references/`).

### Etapa 2.6 📝 — Commit da skill + atualizar README (seção B)
- **Status:** ⬛ Pronta para commit — aguardando aprovação do usuário
- **Ação humana obrigatória:** Sim — aprovar commit.
- **Depende de:** 2.5, 0.2
- **Critério de "feito":** Commit "feat: add refactor-arch skill" criado com aprovação; README atualizado com a seção B) Construção da Skill (decisões de design, anti-patterns escolhidos e por quê, como garantiu agnosticismo, desafios encontrados).

---

## Fase 3 — Execução no Projeto 1 (code-smells-project)

### Etapa 3.1 — Rodar `/refactor-arch` (Fase 1 da skill)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — executar `claude "/refactor-arch"` interativamente dentro de `code-smells-project/`.
- **Depende de:** 2.6
- **Critério de "feito":** Stack (Python/Flask), domínio e nº de arquivos detectados corretamente.
- **Notas / decisões:** Executado pelo usuário diretamente no Claude Code.

### Etapa 3.2 — Observar Fase 2 da skill (auditoria)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não (observação)
- **Depende de:** 3.1
- **Critério de "feito":** ≥5 findings, ≥1 CRITICAL/HIGH, ordenados por severidade, arquivo:linha exatos, segue o template.
- **Notas / decisões:** 13 findings (CRITICAL 5, HIGH 4, MEDIUM 2, LOW 2), seção "Deprecated APIs" presente com declaração explícita de ausência. Ver `reports/audit-project-1.md`.

### Etapa 3.3 — PAUSA: confirmação antes da Fase 3
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim, crítica — ler relatório e decidir y/n.
- **Depende de:** 3.2
- **Critério de "feito":** Decisão registrada com timestamp e racional nas notas.
- **Notas / decisões:** Usuário confirmou `y` e a Fase 3 foi executada.

### Etapa 3.4 — Executar Fase 3 e validar
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — validar manualmente boot + endpoints.
- **Depende de:** 3.3 (somente se `y`)
- **Critério de "feito":** Estrutura MVC criada, app inicia sem erro, endpoints originais respondem, checklist de validação preenchido.
- **Notas / decisões:** Skill reportou boot sem erro e 35 chamadas HTTP comparadas contra a linha de base (ver "Resultado da Refatoração" em `reports/audit-project-1.md`). 9/9 findings CRITICAL/HIGH resolvidos, 4/4 MEDIUM/LOW resolvidos. Validação adicional feita nesta sessão via Docker Compose (ver nota da etapa 3.6).

### Etapa 3.5 — Salvar relatório
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 3.2
- **Critério de "feito":** `reports/audit-project-1.md` criado na raiz do repo com o output real da Fase 2.
- **Notas / decisões:** Salvo em `reports/audit-project-1.md` (138 linhas), com seção final "Resultado da Refatoração" incluindo breaking changes de segurança.

### Etapa 3.6 📝 — Commit do código refatorado + atualizar README (seção C, projeto 1)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — aprovar commit.
- **Depende de:** 3.4, 3.5
- **Critério de "feito":** Commit aprovado; README atualizado com o resumo do relatório do projeto 1 (findings por severidade), comparação antes/depois da estrutura e checklist de validação preenchido para este projeto.
- **Notas / decisões:** Além do código refatorado e do relatório, esta sessão adicionou `Dockerfile`, `docker-compose.yml` e `.dockerignore` ao projeto, e documentou no `code-smells-project/README.md` como subir via `docker compose` e exemplos `curl` para todos os endpoints (públicos, autenticados e admin). **Validado de ponta a ponta nesta sessão:** `docker compose up --build` subiu a aplicação, e cada comando `curl` do README foi executado de fato contra o container (login, CRUD de produto, pedido, relatório de vendas, 401 sem token, reset-db, busca). Um erro foi encontrado e corrigido durante a validação: o exemplo original usava a categoria "periféricos", que não é uma categoria válida — corrigido para "eletronicos". Ambiente de teste derrubado com `docker compose down -v` ao final. Commit `3290957` criado em 2026-10-12 (aprovado pelo usuário), com tudo junto num único commit.

---

## Fase 4 — Execução no Projeto 2 (ecommerce-api-legacy)

### Etapa 4.1 — Copiar a skill para o projeto 2
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 3.6
- **Critério de "feito":** Cópia idêntica em `ecommerce-api-legacy/.claude/skills/refactor-arch/`, sem alterações manuais.
- **Notas / decisões:** Copiada com `cp -R` e verificada com `diff -rq` — cópia idêntica, sem edição manual. Pronta para o usuário rodar `claude "/refactor-arch"` dentro de `ecommerce-api-legacy/`.

### Etapa 4.2 — Rodar `/refactor-arch` (Fases 1 e 2)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — executar comando interativamente.
- **Depende de:** 4.1
- **Critério de "feito":** Stack Node/Express e domínio (LMS/checkout) detectados corretamente; ≥5 findings.
- **Notas / decisões:** Stack e domínio detectados corretamente (Node.js/Express, LMS com checkout). 12 findings: CRITICAL 3 / HIGH 4 / MEDIUM 4 / LOW 1.

### Etapa 4.3 — Observar relatório de auditoria
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 4.2
- **Critério de "feito":** Relatório segue template, ≥1 CRITICAL/HIGH.
- **Notas / decisões:** Relatório completo com severidades justificadas e seção "Deprecated APIs" (sqlite3 em estilo callback). Salvo em `reports/audit-project-2.md`.

### Etapa 4.4 — PAUSA: confirmação antes da Fase 3
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim, crítica.
- **Depende de:** 4.3
- **Notas / decisões:** Usuário confirmou `y` após revisar o relatório.

### Etapa 4.5 — Executar Fase 3 e validar
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — validação manual (sem `/health`; usar `api.http` como roteiro de smoke test).
- **Depende de:** 4.4
- **Notas / decisões:** 7/7 CRITICAL/HIGH resolvidos (com ressalva documentada no AP-08), 5/5 MEDIUM/LOW resolvidos. Validação com 15 chamadas da linha de base + testes de concorrência (20 checkouts simultâneos) relatados no próprio `reports/audit-project-2.md`.

### Etapa 4.6 📝 — Salvar relatório, commit e atualizar README (seção C, projeto 2)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — aprovar commit.
- **Depende de:** 4.3, 4.5
- **Critério de "feito":** `reports/audit-project-2.md` salvo, código refatorado commitado, README atualizado com o resumo do projeto 2 (seção C).
- **Notas / decisões:** Adicionados `Dockerfile`, `docker-compose.yml`, `.dockerignore` e seção "Docker (docker compose)" + "Exemplos de uso (curl)" no `ecommerce-api-legacy/README.md`. Validado end-to-end via `docker compose up --build -d`: checkout (sucesso e recusado), relatório financeiro admin (401 sem token, 200 com token) e delete de usuário (401 sem token, 200 com token) — todas as respostas conferem com o relatório. Seção C do README raiz preenchida para o projeto 2. Aguardando commit único (código refatorado + docker + READMEs + este arquivo).

---

## Fase 5 — Execução no Projeto 3 (task-manager-api)

### Etapa 5.1 — Copiar a skill para o projeto 3
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 4.6
- **Critério de "feito":** Cópia idêntica em `task-manager-api/.claude/skills/refactor-arch/`.
- **Notas / decisões:** Copiada com `cp -R` e verificada com `diff -rq` — cópia idêntica, sem edição manual. Pronta para o usuário rodar `claude "/refactor-arch"` dentro de `task-manager-api/`.

### Etapa 5.2 — Rodar `/refactor-arch` (Fases 1 e 2)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — executar comando interativamente.
- **Depende de:** 5.1
- **Critério de "feito":** Detecta Python/Flask e domínio "Task Manager"; encontra problemas mesmo com organização parcial.
- **Notas / decisões:** Detecção correta, incluindo a observação de que a estrutura existente (models/routes/services/utils) acumula validação/ORM/regra/serialização nas rotas. 11 findings: CRITICAL 3 / HIGH 3 / MEDIUM 3 / LOW 2.

### Etapa 5.3 — Observar relatório de auditoria
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 5.2
- **Notas / decisões:** Relatório completo com 16 ocorrências de `Model.query.get` e 22 de `datetime.utcnow()` listadas na seção "Deprecated APIs". Salvo em `reports/audit-project-3.md`.

### Etapa 5.4 — PAUSA: confirmação antes da Fase 3
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim, crítica.
- **Depende de:** 5.3
- **Notas / decisões:** Usuário confirmou `y` após revisar o relatório.

### Etapa 5.5 — Executar Fase 3 e validar (atenção: melhorar, não recriar)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — validação manual mais cuidadosa (risco maior de regressão em projeto já parcialmente estruturado).
- **Depende de:** 5.4
- **Critério de "feito":** Endpoints continuam respondendo; estrutura reorganizada corretamente (ex.: categorias saem de `report_routes.py`, notification_service usado ou removido com justificativa).
- **Notas / decisões:** 6/6 CRITICAL/HIGH resolvidos, 5/5 MEDIUM/LOW resolvidos. Skill melhorou a estrutura existente em vez de recriar do zero (models mantidos com correções); categorias e login ganharam blueprint próprio; `notification_service.py` (nunca chamado) removido com justificativa documentada. Validação com 68 chamadas da linha de base relatada no próprio `reports/audit-project-3.md`.

### Etapa 5.6 📝 — Salvar relatório, commit e atualizar README (seção C, projeto 3)
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — aprovar commit.
- **Depende de:** 5.3, 5.5
- **Critério de "feito":** `reports/audit-project-3.md` salvo, código refatorado commitado, README atualizado com o resumo do projeto 3 (seção C).
- **Notas / decisões:** Adicionados `Dockerfile`, `docker-compose.yml`, `.dockerignore` e seção "Docker (docker compose)" + "Exemplos de uso (curl)" no `task-manager-api/README.md`. Validado end-to-end via `docker compose up --build -d`: login, tasks (listar/criar/buscar/stats/deletar), categorias, usuários (criar público, listar, deletar admin) e relatórios — todas as respostas conferem com o relatório. Seção C do README raiz preenchida para o projeto 3. Aguardando commit único (código refatorado + docker + READMEs + este arquivo).

---

## Fase 6 — Consolidação de relatórios e evidências

### Etapa 6.1 — Revisar os 3 relatórios
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — revisão editorial de consistência.
- **Depende de:** 3.5, 4.6, 5.6
- **Notas / decisões:** Estrutura já era consistente (Summary/Findings ordenados por severidade/Deprecated APIs/Total/Resultado da Refatoração nos 3). Normalizados pequenos detalhes de formatação: título H1 padronizado (`# Audit — <nome-do-projeto>`) nos 3 relatórios (faltava no 2, estava mais verboso no 3), e a nota "os caminhos se referem ao código legado" movida para a mesma posição (após o bloco de auditoria) nos 3.

### Etapa 6.2 — Preencher checklist de validação
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Não
- **Depende de:** 6.1
- **Critério de "feito":** Checklist das Fases 1/2/3 (challenge.md) preenchido para os 3 projetos.
- **Notas / decisões:** Checklist (texto idêntico ao `challenge.md`) já preenchido e marcado para os 3 projetos nas respectivas subseções da seção C do README raiz (etapas 3.6/4.6/5.6).

### Etapa 6.3 📝 — Capturar evidências (logs/screenshots) e incorporar ao README
- **Status:** ✅ Concluída
- **Ação humana obrigatória:** Sim — rodar as 3 apps refatoradas e capturar prints/curl de boot + endpoints.
- **Depende de:** 3.4, 4.5, 5.5
- **Critério de "feito":** Evidências salvas (ex.: `reports/screenshots/` ou `reports/logs/`) e referenciadas na seção C do README.
- **Notas / decisões:** Logs capturados em `reports/logs/project-{1,2,3}-*.log`: para cada projeto, `docker compose up --build -d`, log de boot completo via `docker compose logs`, e respostas reais de `curl` cobrindo rotas públicas, autenticadas, admin e os casos de erro esperados (`401` sem token). Projeto 1 inclui também a confirmação de que `/admin/query` (removido na refatoração) agora responde 404. Arquivos referenciados na seção C do README raiz, um link por projeto. Containers derrubados (`down`/`down -v`) após a captura.

---

## Fase 7 — README.md: revisão final (não é a primeira redação — seções A/B/C já foram escritas incrementalmente nas etapas 1.4, 2.6, 3.6/4.6/5.6/6.3)

### Etapa 7.1 — Escrever seção D) Como Executar
- **Status:** ⬜ Pendente
- **Ação humana obrigatória:** Não (só revisão)
- **Depende de:** 2.6 (precisa da skill já criada para descrever pré-requisitos/comandos)
- **Critério de "feito":** Seção D com pré-requisitos, comandos por projeto e como validar.

### Etapas 7.2–7.4 — Revisão final de consistência/tom das seções A/B/C/D
- **Status:** ⬜ Pendente
- **Ação humana obrigatória:** Sim — revisão final de conteúdo e tom antes de publicar.
- **Depende de:** Fases 1–6 completas, 7.1
- **Critério de "feito":** README contém as 4 seções obrigatórias (Análise Manual, Construção da Skill, Resultados, Como Executar), já escritas incrementalmente, apenas revisadas/polidas nesta etapa — sem redação do zero.

---

## Fase 8 — Entrega final

### Etapa 8.1 — Revisar git status/diff completo
- **Status:** ⬜ Pendente
- **Ação humana obrigatória:** Não (recomendável revisão)
- **Depende de:** 7.4

### Etapa 8.2 — Push para origin/main
- **Status:** ⬜ Pendente
- **Ação humana obrigatória:** Sim, crítica — autorizar push explicitamente. Nunca force-push.
- **Depende de:** 8.1

### Etapa 8.3 — Verificação pública no GitHub
- **Status:** ⬜ Pendente
- **Ação humana obrigatória:** Sim — checagem visual (skill nos 3 projetos, reports/ na raiz, README renderizado).
- **Depende de:** 8.2
