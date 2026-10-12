# Guidelines de Arquitetura — Alvo MVC (Fase 3)

Define o alvo para onde a Fase 3 converge. Independente da stack, o resultado precisa ter as mesmas camadas com as mesmas responsabilidades — o nome da pasta muda conforme a convenção do framework, a responsabilidade não.

## 1. Camadas e responsabilidades

| Camada | Responsabilidade | NÃO deve fazer |
|---|---|---|
| **Models** | Representar a entidade e acessar dados (persistir/consultar). Um módulo por entidade. | Nenhuma lógica de HTTP, nenhum roteamento, nenhuma regra de negócio pesada. |
| **Views / Routes** | Declarar rotas, interpretar a requisição, formatar a resposta. Camada fina. | Nenhuma regra de negócio, nenhum SQL direto. |
| **Controllers** | Orquestrar uma requisição: validar entrada, chamar services/models, montar a resposta. | Nenhum SQL, nenhuma regra de negócio pesada embutida. |
| **Services** | Regra de negócio (cálculo de preço/estoque, checkout, emissão de token, notificação). | Nenhum objeto de request/response HTTP. |
| **Config** | Carregar configuração/segredos a partir do ambiente. | Nenhum segredo hardcoded. |
| **Middlewares** | Preocupações transversais: tratamento de erro centralizado, autenticação, logging. | Nenhuma regra de negócio específica de uma rota. |
| **Entry point** | Composition root: conectar as camadas, iniciar o servidor. | Nenhuma lógica de negócio. |

## 2. Direção de dependência

A dependência flui em **uma única direção** — da camada externa para a interna, nunca o contrário:

```
Routes/Views  →  Controllers  →  Services  →  Models  →  Banco de dados
                                     ↑
                      Config injetado aqui         Middlewares envolvem o pipeline
```

- Um **Model** nunca importa um Controller ou uma Route.
- Uma **Route** nunca executa SQL ou regra de negócio diretamente.
- Segredos vêm de **Config**, injetados — nunca lidos ad-hoc dentro de um model.

## 3. Estrutura de diretórios de referência

Adapte o nome ao idioma do framework (`views/` para blueprints Flask, `routes/` para routers Express) — ambos mapeiam para o mesmo conjunto de camadas:

```
src/
├── config/            # configurações/segredos lidos do ambiente
├── database/          # conexão (por requisição/pool) + schema/seed
├── models/            # um módulo por entidade — acesso a dados parametrizado
├── services/          # regras de negócio
├── controllers/       # orquestração da requisição
├── views/ | routes/   # declaração de rotas (blueprints / routers)
├── middlewares/        # error handler central, autenticação, logging
└── app.py | app.js     # composition root (entry point)
```

**Equivalências Flask ↔ Express:** blueprint Flask == router Express (Views/Routes); conexão por requisição (`flask.g`) == handle de banco escopado por requisição no Express; `werkzeug.security` == `bcrypt`; `@app.errorhandler` == middleware de erro `(err, req, res, next)`.

## 4. Estratégia adaptativa (profundidade depende da Fase 1)

A profundidade da refatoração **depende da arquitetura atual** identificada na Fase 1:

- **Monolítico** (tudo em poucos arquivos, God Class/Module) → construir o scaffold MVC completo acima, do zero, movendo cada responsabilidade para sua camada.
- **Já em camadas** (pastas como `models/`, `routes/`, `services/`, `utils/` já existem) → fazer melhoria **direcionada**: corrigir os anti-patterns encontrados e preencher o que falta (módulo de config, services reais, error handler, autenticação) **sem reescrever o que já está adequado**. Não gere churn em código que já funciona só por uniformidade estética.

Em **ambos** os casos:
- O **contrato externo dos endpoints é preservado** — mesmos paths, mesmos métodos, mesmas respostas de sucesso. A exceção é correção de segurança (ver regra 4 do `SKILL.md`): remover campo sensível de uma resposta, ou exigir autenticação onde antes não havia, são mudanças aceitáveis e devem ser documentadas como *breaking change*.
- Configuração é extraída (sem segredo hardcoded), models abstraem dados, routes/views são separadas da lógica, controllers concentram o fluxo, o tratamento de erro é centralizado, e existe um entry point claro.

## 5. Definição de "feito" (estrutura)

Um projeto refatorado satisfaz:
- [ ] Módulo de config, sem segredo hardcoded.
- [ ] Models abstraem acesso a dados (parametrizado/ORM), sem regra de negócio.
- [ ] Views/Routes separadas da lógica.
- [ ] Controllers concentram o fluxo da requisição.
- [ ] Regras de negócio vivem em Services.
- [ ] Tratamento de erro centralizado.
- [ ] Entry point claro (composition root).
- [ ] Aplicação inicia sem erro e os endpoints originais continuam respondendo.
