# Catálogo de Anti-Patterns (Fase 2)

Base de conhecimento que a Fase 2 cruza contra o código real. Cada entrada tem um **ID estável**, uma **severidade padrão**, um **sinal de detecção concreto** (algo que se pode apontar no código, não "código ruim"), o **impacto** e a **correção**, expandida com exemplo de código no `refactoring-playbook.md`.

Escala de severidade (do desafio):

| Severidade | Significado |
|---|---|
| **CRITICAL** | Falha grave de arquitetura/segurança: impede funcionamento correto, expõe dado sensível, ou destrói completamente a separação de responsabilidades. |
| **HIGH** | Violação forte de MVC/SOLID que dificulta muito manutenção/teste. |
| **MEDIUM** | Padronização, duplicação, ou gargalo de performance moderado. |
| **LOW** | Legibilidade, nomenclatura, magic numbers. |

A severidade da tabela é o padrão — suba ou desça um nível quando o impacto real do caso concreto justificar (ex.: um N+1 em uma rota de alto tráfego pode subir para HIGH).

Toda ocorrência relatada precisa de `arquivo:linha` real, lido no código. Agrupe achados da mesma causa raiz em um único finding em vez de inflar a contagem.

---

## AP-01 — SQL Injection por concatenação de string — `CRITICAL`

**Sinal de detecção:** `execute("..." + variavel)`, f-string/template string dentro de uma query SQL, `query += " AND campo = '" + valor + "'"`.
**Por que importa:** entrada do usuário se torna código SQL — permite bypass de autenticação, exfiltração e destruição de dados (OWASP Top 10 #1).
**Correção:** queries parametrizadas (placeholders `?`/`%s` + tupla de parâmetros), nunca concatenação. → Playbook RP-02.

## AP-02 — Segredos hardcoded e debug/CORS inseguros — `CRITICAL`

**Sinal de detecção:** literal `SECRET_KEY = "..."`, chave de API/pagamento, senha de SMTP/banco no código-fonte; `DEBUG = True` ou CORS sem restrição de origem em um app que se diz "produção".
**Por que importa:** segredo versionado vaza para qualquer um com acesso ao repositório/histórico; debugger exposto em produção é RCE; CORS aberto facilita exfiltração cross-origin.
**Correção:** carregar de variável de ambiente, nunca commitar o valor real, `DEBUG` default `false`, CORS restrito a origens conhecidas. → Playbook RP-01.

## AP-03 — Endpoint de execução arbitrária — `CRITICAL`

**Sinal de detecção:** rota que recebe um comando/SQL livre do corpo da requisição e executa sem validação de conteúdo nem de identidade (`cursor.execute(request_body["sql"])`); rota administrativa destrutiva (`reset-db`) sem nenhuma autenticação.
**Por que importa:** controle total do banco/sistema para qualquer chamador externo — é o pior caso de AP-01 combinado com ausência total de autorização.
**Correção:** remover o endpoint genérico; expor apenas casos de uso específicos e validados, atrás de autenticação/autorização. → Playbook RP-03.

## AP-04 — Exposição de dado sensível na resposta/log — `CRITICAL`

**Sinal de detecção:** campo `senha`/`password` (mesmo com hash) presente no `to_dict()`/serializador devolvido pela API; segredo/chave reimpresso em uma resposta JSON (ex.: endpoint de health); número de cartão ou chave de gateway escritos em `console.log`/`print`.
**Por que importa:** mesmo um hash de senha vazado facilita ataques offline; segredo reexposto por um endpoint de diagnóstico anula qualquer proteção dele em outro lugar.
**Correção:** serializador/DTO explícito que nunca inclui campos sensíveis; nunca logar segredo ou dado de pagamento. → Playbook RP-04.

## AP-05 — Criptografia quebrada / hashing inseguro de senha — `CRITICAL`

**Sinal de detecção:** senha em texto plano comparada diretamente; `hashlib.md5(...)`/`sha1` para senha; "hash" artesanal feito de repetição de base64 (reversível, sem salt).
**Por que importa:** MD5/SHA1 e esquemas artesanais são quebrados/reversíveis — um vazamento do banco expõe todas as senhas originais.
**Correção:** hash de senha dedicado e com salt (`werkzeug.security.generate_password_hash`, `bcrypt`, `argon2`), nunca um hash genérico de propósito geral. → Playbook RP-05.

## AP-06 — God Class / God Module — `HIGH`

**Sinal de detecção:** um único arquivo/classe que abre a conexão do banco, define schema/seed, registra rotas e contém a regra de negócio de múltiplos domínios ao mesmo tempo.
**Por que importa:** zero separação MVC, impossível testar em isolamento, qualquer mudança arrisca o sistema inteiro.
**Correção:** dividir em Models/Controllers/Services/Routes por domínio, com injeção de dependência. → Playbook RP-06.

## AP-07 — Lógica de negócio na camada errada — `HIGH`

**Sinal de detecção:** cálculo de preço/estoque/desconto dentro do model (que deveria só persistir/consultar); decisão de pagamento, envio de notificação ou orquestração dentro do controller/rota; a mesma regra de negócio (ex.: "tarefa atrasada") reimplementada em 3+ lugares em vez de centralizada.
**Por que importa:** viola SRP — regra de negócio presa na camada errada não pode ser reutilizada nem testada isoladamente, e duplicada ela diverge silenciosamente com o tempo.
**Correção:** extrair a regra para uma camada de Service (ou para o método do model, quando já existir e estiver sendo ignorado), e fazer as rotas/controllers chamarem essa única fonte. → Playbook RP-07.

## AP-08 — Autenticação ausente ou fictícia / autorização ausente — `HIGH`

**Sinal de detecção:** token previsível/não assinado (`"fake-jwt-token-" + id`); nenhuma rota sensível (escrita, leitura de dado de outro usuário, relatório, administração) exige credencial; existe um método de checagem de papel (`is_admin()`) que nunca é chamado por nenhuma rota.
**Por que importa:** qualquer pessoa pode executar ações privilegiadas sem provar identidade.
**Correção:** emissão de token real e assinado com expiração, middleware/decorator de autenticação aplicado de forma consistente a toda rota sensível do recurso — não só a algumas. → Playbook RP-08.

## AP-09 — Estado global mutável — `HIGH`

**Sinal de detecção:** conexão de banco em variável de módulo reaproveitada entre requisições; cache/contador global exportado e mutado por qualquer parte do código; singleton manual sem gestão de ciclo de vida.
**Por que importa:** condição de corrida e acoplamento oculto sob concorrência; difícil de testar; estado que deveria ser por-requisição vaza entre requisições.
**Correção:** conexão por requisição (ou pool) injetada, sem variável global mutável compartilhada. → Playbook RP-09.

## AP-10 — Queries N+1 — `MEDIUM`

**Sinal de detecção:** uma query dentro de um loop `for`/`forEach`; `Model.query.get(id)` chamado por linha em vez de JOIN/eager load; busca aninhada (uma consulta para a lista, outra por item da lista, outra por sub-item).
**Por que importa:** latência cresce linearmente com o volume de dados — uma requisição se transforma em centenas de round-trips ao banco.
**Correção:** uma única consulta com JOIN, ou eager loading do ORM (`joinedload`). → Playbook RP-10.

## AP-11 — Validação/serialização duplicada e código morto — `MEDIUM`

**Sinal de detecção:** o mesmo bloco de validação copiado em criar e atualizar; uma entidade serializada manualmente campo a campo em várias rotas enquanto já existe um `to_dict()`/validador utilitário sendo ignorado; função/serviço definido mas nunca chamado em nenhum lugar do código.
**Por que importa:** regras divergem silenciosamente ao longo do tempo; qualquer mudança de regra exige caçar todas as cópias; utilitário morto confunde quem lê o código.
**Correção:** um único validador/serializador reutilizado em todas as rotas; remover código comprovadamente morto. → Playbook RP-11.

## AP-12 — Uso de APIs/padrões deprecated — `MEDIUM`

**Sinal de detecção:** driver/API 100% baseada em callback quando a mesma biblioteca já oferece Promises/async-await (ex.: `sqlite3` callback-style); método de ORM marcado como legado nas notas de versão (ex.: `Query.get(id)` em versões recentes do SQLAlchemy em favor de `db.session.get(Model, id)`); import de módulo/flag de configuração removido em versão mais recente do framework.
**Por que importa:** APIs deprecated tendem a ser removidas em futuras atualizações, acumulam warnings de runtime e, no caso de callbacks aninhados, favorecem os próprios bugs de tratamento de erro do AP-09/callback hell.
**Correção:** migrar para o equivalente moderno suportado pela versão instalada da dependência, documentando a mudança de comportamento, se houver. → Playbook RP-12.

## AP-13 — Magic numbers e nomenclatura ruim — `LOW`

**Sinal de detecção:** limite numérico sem nome (`if faturamento > 10000`, `if len(nome) > 200`); variável de uma letra em um fluxo de negócio (`u`, `e`, `cc`); lista de status/categoria repetida inline em vários arquivos em vez de uma constante única.
**Por que importa:** a intenção do valor fica implícita; mudar a regra exige caçar o número em todo o código.
**Correção:** extrair para constantes nomeadas/configuração, nomes de domínio em vez de abreviações. → Playbook RP-13.

## AP-14 — Tratamento de erro genérico que vaza detalhe interno — `LOW`

**Sinal de detecção:** `except Exception as e: return jsonify({"erro": str(e)})` ou `catch(err) { res.send(err) }` repetido por toda a camada de rotas, devolvendo mensagem/stack interno ao cliente.
**Por que importa:** vaza informação de implementação útil para um atacante e produz uma experiência de erro inconsistente para o cliente da API.
**Correção:** tratamento de erro centralizado (middleware/error handler) que loga o detalhe internamente e devolve uma mensagem padronizada e segura ao cliente. → Playbook RP-14.

---

## Resumo de severidades do catálogo

| Severidade | Quantidade | IDs |
|---|---|---|
| CRITICAL | 5 | AP-01, AP-02, AP-03, AP-04, AP-05 |
| HIGH | 4 | AP-06, AP-07, AP-08, AP-09 |
| MEDIUM | 3 | AP-10, AP-11, AP-12 |
| LOW | 2 | AP-13, AP-14 |

14 anti-patterns no total, cobrindo segurança, arquitetura/MVC/SOLID, performance, duplicação, uso de API deprecated e qualidade de código — acima do mínimo de 8 exigido pelo desafio.
