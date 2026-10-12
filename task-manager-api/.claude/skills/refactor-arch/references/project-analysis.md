# Análise de Projeto — Heurísticas (Fase 1)

Objetivo da Fase 1: descrever o projeto como ele é hoje, sem julgamento de qualidade. O julgamento vem na Fase 2.

## Ordem de evidência

Não adivinhe a stack pelo nome da pasta. Siga esta ordem, da evidência mais barata para a mais cara:

1. **Manifesto de dependências** — `requirements.txt`, `pyproject.toml`, `package.json` + lockfile. Isso dá linguagem, framework e versão.
2. **Entry point** — `app.py`, `main.py`, `src/app.js`, o script que de fato sobe o servidor (procure `.run(`, `.listen(`, `if __name__ == "__main__"`).
3. **Registro de rotas** — decorators (`@app.route`, blueprints) ou chamadas (`app.get`, `app.post`, `router.use`) revelam a superfície HTTP e ajudam a inferir o domínio.
4. **Camada de dados** — import de driver SQL, ORM (`sqlite3`, `SQLAlchemy`, `db.Model`), criação de schema/seed revelam as entidades e o banco.
5. **Configuração e middlewares** — leitura de variáveis de ambiente, CORS, error handlers.

Quando um arquivo só repassa/registra comportamento (ex.: `app.py` que só importa e registra blueprints), siga um passo adiante até achar a função que de fato processa ou persiste o dado.

## Detecção de linguagem/framework

- Python + import de `flask`/`flask_cors` → Flask. Confirme a versão no `requirements.txt`.
- JavaScript + `require('express')`/`import express` ou uso de `app.get/post/use` → Express. Confirme no `package.json`.
- Não chame um projeto de "MVC" só porque existem pastas `models/`/`routes/` — isso é nome de pasta, não separação de responsabilidade. Verifique se cada arquivo realmente só faz o que seu nome promete (ver seção de mapeamento de arquitetura).

## Banco de dados

- Driver bruto (`sqlite3`, `pg`, `mysql2`) sem ORM → queries manuais, maior risco de SQL injection.
- ORM (`SQLAlchemy`, `Sequelize`, `Prisma`) → menor risco de injection, mas ainda pode ter N+1, falta de transação, ou serialização que expõe campos sensíveis.
- Liste as tabelas/models encontrados e, quando possível, as relações entre eles (ex.: `usuarios -> pedidos -> itens_pedido -> produtos`).

## Inferência de domínio

Infira o domínio da aplicação a partir de nomes de rota, nomes de tabela/entidade, dados de seed e vocabulário das respostas (`"mensagem"`, `"produto"`, `"curso"`, `"task"`). Se a evidência for ambígua, declare a incerteza em vez de inventar uma certeza.

## Mapeamento de arquitetura atual

Para cada arquivo de código-fonte relevante, classifique sua responsabilidade **efetiva** (o que o código faz), não a responsabilidade nominal (o nome do arquivo/pasta):

| Papel | O que procurar |
|---|---|
| Composition root | construção do app, wiring de dependências, `app.run`/`app.listen` |
| Rotas/Views | declaração de método+path, parsing de request, status/formato de resposta |
| Controllers | orquestração do caso de uso, chamando services/models |
| Models/Repositórios | SQL/ORM, mapeamento de persistência |
| Services | regra de negócio pura (preço, estoque, pagamento, notificação) |
| Config | leitura de env vars, segredos, portas |
| Middlewares | autenticação, validação, tratamento de erro centralizado |

Descreva a cadeia de dependência observada (ex.: `app.py → controllers.py → models.py → SQLite`) e aponte violações encontradas (ex.: "a rota executa SQL direto", "o model monta resposta HTTP").

## Contagem de arquivos e linhas

Conte apenas arquivos de código-fonte mantidos pelo projeto. Exclua `.git`, `venv`/`node_modules`, `__pycache__`, arquivos de banco (`*.db`), a própria pasta `.claude/skills/`, e qualquer artefato gerado. Use `wc -l`/`find` de verdade — não estime.

## Saída da Fase 1

Imprima exatamente este bloco, preenchido com dados reais (nunca invente um número):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework> <versão, se encontrada>
Dependencies:  <dependências relevantes, separadas por vírgula>
Domain:        <domínio inferido>
Architecture:  <classificação curta: monolítica / parcialmente organizada / em camadas> — <uma frase explicando por quê>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas/entidades>
================================
```

Não emita findings de qualidade aqui — isso é tarefa da Fase 2.
