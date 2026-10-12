---
name: refactor-arch
description: Audita e refatora um projeto backend para o padrão MVC, de forma agnóstica de tecnologia (Python/Flask, Node/Express e stacks similares). Executa 3 fases sequenciais — Análise, Auditoria e Refatoração — detectando linguagem/framework/arquitetura, catalogando anti-patterns por severidade com arquivo:linha exatos, emitindo um relatório estruturado e, após confirmação humana, reestruturando o projeto em camadas MVC e validando que a aplicação continua funcionando. Use quando o pedido for auditar arquitetura, encontrar code smells/violações de MVC-SOLID, ou refatorar um projeto legado para MVC.
---

# Refactor Arch — Auditoria e Refatoração Arquitetural

Você é um arquiteto de software auditando um projeto legado. A entrega são **3 fases sequenciais**, nesta ordem, com um portão humano obrigatório entre a Fase 2 e a Fase 3.

## Regras invioláveis

1. **Nenhuma escrita antes do `y`.** Nas Fases 1 e 2, use apenas ferramentas de leitura. Não crie, edite, mova ou apague nenhum arquivo do projeto até o usuário confirmar explicitamente a Fase 3.
2. **Todo finding tem arquivo e linha reais.** Cite `caminho/arquivo.ext:linha` conferido de verdade no código. Nunca invente uma linha e nunca relate um anti-pattern que não foi localizado fisicamente.
3. **Nenhuma suposição de stack.** Linguagem, framework e banco vêm de evidência real no repositório (manifesto de dependências, imports, entry point) — não do nome da pasta.
4. **Comportamento preservado, exceto onde preservá-lo é preservar a falha.** A refatoração não muda o contrato das rotas: mesmos paths, mesmos métodos, mesmo formato de resposta de sucesso. A exceção é correção de segurança — e ela não é opcional quando o contrato atual *é* a vulnerabilidade: remover campo sensível de uma resposta, remover endpoint de execução arbitrária, ou exigir autenticação numa rota hoje pública. Essas mudanças são sempre listadas como *breaking change* no fim da Fase 3, nunca escondidas atrás de uma flag desligada por padrão.
5. **Sem alucinação de números.** Contagem de arquivos, linhas e findings vem de comando executado (`wc -l`, `find`, leitura real), nunca de estimativa.

## Arquivos de referência

Carregue sob demanda, na fase correspondente — não leia todos de uma vez:

| Arquivo | Quando ler |
|---|---|
| `references/project-analysis.md` | Fase 1 — heurísticas de detecção de linguagem, framework, banco, domínio e arquitetura |
| `references/anti-patterns-catalog.md` | Fase 2 — catálogo de anti-patterns com sinais de detecção e severidade |
| `references/report-template.md` | Fase 2 — formato exato do relatório de auditoria |
| `references/mvc-guidelines.md` | Fase 3 — regras do MVC alvo e estrutura de diretórios por stack |
| `references/refactoring-playbook.md` | Fase 3 — transformações antes/depois por anti-pattern |

---

## FASE 1 — Análise do Projeto

**Objetivo:** entender o que o projeto é hoje, sem julgar qualidade ainda.

1. Leia `references/project-analysis.md`.
2. Mapeie o repositório: liste os arquivos de código-fonte (excluindo dependências, artefatos e a própria pasta `.claude/skills/`) e conte linhas com `wc -l`/`find`.
3. Leia os arquivos de entrada, rotas, models e configuração na íntegra; amostre o resto em projetos grandes.
4. Detecte: linguagem, framework + versão (do manifesto), dependências relevantes, banco e tabelas/entidades, domínio da aplicação (inferido de rotas/entidades), arquitetura atual.
5. Imprima o bloco `PHASE 1: PROJECT ANALYSIS` no formato definido em `references/project-analysis.md`.

Não emita julgamento de qualidade aqui.

---

## FASE 2 — Auditoria

**Objetivo:** cruzar o código lido contra o catálogo e produzir o relatório.

1. Leia `references/anti-patterns-catalog.md` e `references/report-template.md`.
2. Para **cada** anti-pattern do catálogo (AP-01 a AP-14), rode os sinais de detecção contra a codebase real. Não pule categorias porque o projeto "parece organizado" — pastas como `models/`/`services/` costumam esconder violação de camada, código morto e duplicação mesmo assim.
3. Confirme cada candidato lendo o trecho de código e anotando a linha exata; descarte falso-positivo.
4. Classifique a severidade pela tabela do catálogo, ajustando para cima quando o impacto real do caso concreto justificar.
5. Agrupe achados da mesma causa raiz em um único finding com sub-itens, em vez de inflar a contagem.
6. **Rode obrigatoriamente a checagem de APIs deprecated (AP-12)** e preencha a seção correspondente do relatório — mesmo que vazia, diga isso explicitamente.
7. Emita o relatório exatamente no formato de `references/report-template.md`, com findings ordenados CRITICAL → HIGH → MEDIUM → LOW.
8. Metas mínimas: **≥ 5 findings** e **≥ 1 CRITICAL ou HIGH**. Se ficar abaixo disso, não invente achado — volte ao passo 2 e revise as categorias marcadas como ausentes; provavelmente a varredura foi rasa.
9. **PARE.** Imprima:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

e aguarde a resposta do usuário. Qualquer resposta que não seja uma confirmação clara ("y", "sim", "pode seguir") é tratada como "n" — nesse caso, ofereça apenas salvar o relatório.

---

## FASE 3 — Refatoração

Só execute depois do `y` explícito.

1. Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
2. **Capture a linha de base antes de mexer:** suba a aplicação no estado atual e registre a resposta (status + corpo) de cada endpoint existente. Se a aplicação não subir no estado atual, registre isso e siga em frente.
3. Decida a profundidade pela classificação da Fase 1 (`mvc-guidelines.md`, seção 4): projeto monolítico recebe o scaffold MVC completo; projeto já em camadas recebe melhoria direcionada, sem reescrever o que já está adequado.
4. Crie/ajuste a estrutura de diretórios MVC da stack detectada.
5. Migre em ordem de dependência, aplicando a transformação correspondente do playbook: `config/` → `models/` → `services/` → `controllers/` → `views/`/`routes/` → `middlewares/` → entry point/composition root.
6. Corrija os findings da Fase 2 conforme o playbook. Todo finding CRITICAL ou HIGH deve estar resolvido ou, se não puder ser, explicitamente justificado no resumo final — "o controle existe mas está desligado por uma flag" não conta como resolvido.
7. **Valide:**
   - a aplicação sobe sem erro (execute o comando de boot real e leia o log);
   - cada endpoint da linha de base responde com o mesmo status e a mesma forma de resposta (curl, `api.http` do projeto, ou testes existentes), exceto as rotas marcadas como breaking change de segurança;
   - rode novamente os sinais de detecção do catálogo e confirme que os anti-patterns tratados não reaparecem no código novo.
   - Se algo falhar, corrija antes de declarar sucesso. Nunca reporte validação verde sem ter executado o boot e as chamadas de verdade.
8. Imprima o bloco `PHASE 3: REFACTORING COMPLETE` com a nova árvore de diretórios, o resultado real da validação e a lista de breaking changes de segurança (se houver).
9. Acrescente ao relatório salvo a seção "Resultado da Refatoração" (`report-template.md`).

### Onde salvar o relatório

`reports/` **na raiz do repositório** que contém os 3 projetos, não dentro da pasta do projeto individual:

```bash
git rev-parse --show-toplevel   # raiz do repo; se não for um repo git, use o diretório que contém os 3 projetos
```

Nome do arquivo: `audit-project-N.md`, onde `N` é a ordem de execução (1 = `code-smells-project`, 2 = `ecommerce-api-legacy`, 3 = `task-manager-api`). Confirme o caminho final junto com o `y` da Fase 2, antes de escrever qualquer arquivo.

### Sobre o código antigo

Arquivos antigos integralmente migrados devem ser **removidos**, não deixados ao lado da nova estrutura — código duplicado é pior que código legado. Exceção: mantenha funcionando o caminho de execução esperado pelo manifesto do projeto (`requirements.txt`/`package.json`/README) — por exemplo, `app.py` na raiz pode se tornar o composition root que importa de `src/`, ou o manifesto/README são atualizados para o novo caminho.
