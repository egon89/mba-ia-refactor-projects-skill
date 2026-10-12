# Template de Relatório de Auditoria (Fase 2)

Use exatamente esta estrutura para a saída da Fase 2. Não é um sugestão de formato — é o contrato que o relatório salvo em `reports/audit-project-N.md` deve seguir.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analisados | ~<LOC> linhas de código

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

## Findings

### [CRITICAL] <Nome do Anti-Pattern> (<AP-ID>)
File: <caminho>:<linha> ou <caminho>:<inicio>-<fim>
Description: <o que foi encontrado, em termos concretos>
Impact: <por que isso importa — consequência real>
Recommendation: <correção específica, referenciando o playbook>

### [HIGH] <Nome do Anti-Pattern> (<AP-ID>)
File: ...
Description: ...
Impact: ...
Recommendation: ...

(repita para todos os findings, SEMPRE ordenados CRITICAL → HIGH → MEDIUM → LOW)

## Deprecated APIs
<liste cada ocorrência de AP-12 encontrada, com arquivo:linha e o equivalente moderno recomendado.
Se nenhuma for encontrada, escreva explicitamente: "Nenhuma API deprecated detectada.">

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras de preenchimento

- Todo finding **precisa** de `arquivo:linha` real, lido no código — nunca invente uma linha.
- Mínimo de **5 findings** por projeto.
- Pelo menos **1 CRITICAL ou HIGH** entre os findings.
- A seção "Deprecated APIs" é obrigatória mesmo quando vazia — declare a ausência explicitamente, não omita a seção.
- Agrupe ocorrências da mesma causa raiz em um único finding com sub-itens (ex.: "SQL Injection em 12 pontos de `models.py`, listados abaixo") em vez de inflar a contagem total.
- Nunca inicie a Fase 3 sem a confirmação explícita (`y`) do usuário a esta pergunta final.

## Ao salvar o relatório (depois da confirmação)

Destino: `reports/audit-project-N.md` **na raiz do repositório** (não dentro da pasta do projeto). `N` segue a ordem de execução: projeto 1 = `code-smells-project`, projeto 2 = `ecommerce-api-legacy`, projeto 3 = `task-manager-api`.

Depois da Fase 3, o relatório salvo é acrescido de uma seção final:

```
## Resultado da Refatoração
- Estrutura MVC criada: <resumo da árvore de diretórios>
- Validação: <aplicação sobe sem erro? endpoints originais respondem?>
- Findings CRITICAL/HIGH resolvidos: <N>/<N>
- Breaking changes de segurança (se houver): <lista>
```
