# Playbook de Refatoração (Fase 3)

Transformações concretas da Fase 3. Cada padrão resolve um ou mais anti-patterns do catálogo e traz exemplo de código antes/depois. Os exemplos alternam entre Python e JavaScript de propósito — o que importa é a movimentação estrutural, não a sintaxe; traduza para a linguagem do projeto.

---

## RP-01 — Extrair segredos/config para o ambiente

Resolve **AP-02**. Faça isso primeiro — as transformações seguintes dependem de existir um lugar para a configuração ir.

**Antes**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
app.run(host="0.0.0.0", port=5000, debug=True)
```

**Depois**
```python
# config/settings.py
import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5000"))

settings = Settings()
```
```bash
# .env.example
SECRET_KEY=replace-with-a-random-value
DEBUG=false
```
O segredo que estava no código já vazou — além de removê-lo, registre no relatório que ele precisa ser rotacionado em produção.

---

## RP-02 — Parametrizar queries

Resolve **AP-01**.

**Antes**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
)
```

**Depois**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute(
    "SELECT * FROM usuarios WHERE email = ?", (email,)
)
# comparação de senha acontece depois, contra o hash (ver RP-05), nunca dentro do SQL
```
Para queries dinâmicas (filtros opcionais), monte a cláusula e acumule os parâmetros à parte:
```python
def buscar_produtos(termo=None, categoria=None):
    sql = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        sql += " AND (nome LIKE ? OR descricao LIKE ?)"
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    cursor.execute(sql, params)
```

---

## RP-03 — Remover endpoints de execução arbitrária

Resolve **AP-03**.

**Antes**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = request.get_json().get("sql", "")
    cursor.execute(query)   # SQL livre, sem autenticação
```

**Depois**
```python
# o endpoint genérico é removido. Em seu lugar, casos de uso específicos,
# cada um validado e atrás de autenticação/autorização:
@app.route("/produtos/busca", methods=["GET"])
@require_auth
def buscar_produtos():
    return jsonify(ProdutoService.buscar(request.args.get("termo")))
```
Se existir uma necessidade legítima de consulta ad-hoc (ex.: suporte interno), ela vira uma ferramenta operacional fora da API pública, nunca uma rota HTTP exposta.

---

## RP-04 — Serializadores/DTOs explícitos (sem campo sensível)

Resolve **AP-04**.

**Antes**
```python
def to_dict(self):
    return {
        "id": self.id, "nome": self.name,
        "email": self.email, "password": self.password,  # nunca deveria sair daqui
    }
```

**Depois**
```python
def to_dict(self):
    return {"id": self.id, "nome": self.name, "email": self.email}
    # password/hash nunca é serializado; se algum fluxo (ex.: debug) precisar do hash,
    # use um método separado e explícito, nunca o serializador público.
```
Aplique a mesma regra a logs: nunca `print`/`console.log` de número de cartão, chave de API ou senha — nem mesmo mascarados em texto livre.

---

## RP-05 — Hash de senha vetorizado

Resolve **AP-05**.

**Antes (Python, MD5 sem salt)**
```python
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()
```

**Antes (JS, "hash" artesanal reversível)**
```javascript
function badCrypto(pwd) {
    let hash = "";
    for (let i = 0; i < 10000; i++) hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    return hash.substring(0, 10);
}
```

**Depois**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```
```javascript
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(pwd, 10);
const ok = await bcrypt.compare(pwd, hash);
```

---

## RP-06 — Dividir God Class / God Module em camadas

Resolve **AP-06**.

**Antes**
```javascript
class AppManager {
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  initDb() { /* schema + seed */ }
  setupRoutes(app) { /* checkout + relatório + delete, tudo aqui */ }
}
```

**Depois**
```javascript
// database/connection.js       -> conexão/schema/seed
// models/enrollmentModel.js    -> acesso a dados de matrícula
// services/checkoutService.js  -> regra de negócio do checkout
// controllers/checkoutController.js -> orquestra: valida entrada, chama o service, responde
// routes/checkoutRoutes.js     -> só declara a rota e aponta pro controller
router.post('/api/checkout', checkoutController.checkout);
```
Cada arquivo passa a ter uma única razão para mudar.

---

## RP-07 — Mover regra de negócio para o Service

Resolve **AP-07**.

**Antes**
```python
# dentro do controller
def criar_pedido():
    for item in itens:
        produto = buscar_produto(item["produto_id"])
        if produto["estoque"] < item["quantidade"]:
            return jsonify({"erro": "sem estoque"}), 400
        total += produto["preco"] * item["quantidade"]
    # ... além disso, "envia" email/SMS direto aqui
```

**Depois**
```python
# services/pedido_service.py
class PedidoService:
    @staticmethod
    def criar(usuario_id, itens):
        total = PedidoService._validar_estoque_e_calcular_total(itens)
        pedido = PedidoModel.criar(usuario_id, itens, total)
        NotificationService.notificar_pedido_criado(pedido)
        return pedido

# controllers/pedido_controller.py
def criar_pedido():
    pedido = PedidoService.criar(request.json["usuario_id"], request.json["itens"])
    return jsonify(pedido), 201
```
O mesmo vale para lógica duplicada (ex.: "tarefa atrasada" calculada em 4 lugares): ela passa a existir em um único método do Service/Model, e todo o resto chama esse método.

---

## RP-08 — Autenticação real + gate de autorização

Resolve **AP-08**.

**Antes**
```python
return jsonify({"token": "fake-jwt-token-" + str(user.id)})
# nenhuma rota verifica token
```

**Depois**
```python
import jwt, datetime

def login():
    # ... valida credenciais ...
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)},
        settings.SECRET_KEY, algorithm="HS256",
    )
    return jsonify({"token": token})

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        try:
            request.user = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except Exception:
            return jsonify({"erro": "não autorizado"}), 401
        return fn(*args, **kwargs)
    return wrapper

@app.route("/usuarios/<id>", methods=["DELETE"])
@require_auth
@require_admin
def deletar_usuario(id): ...
```
Aplique o decorator/middleware de forma consistente: se uma rota de escrita do recurso exige autenticação, todas as rotas de escrita do mesmo recurso exigem — não só a mais "perigosa".

**Autenticação não é autorização.** Exigir um token válido garante *quem* está fazendo a requisição, não *o que* essa pessoa pode acessar. Toda rota identificada por id que exponha ou mute um registro ligado a um usuário específico precisa, além do token, de uma checagem de posse do recurso (**owner-or-admin**): só o próprio dono ou um admin passa; qualquer outro usuário autenticado recebe `403`, não `200`.

**Antes** (token exigido, mas sem checagem de dono — qualquer usuário autenticado lê/altera/apaga registro de outro)
```python
@task_bp.before_request(authenticate_request)  # só confere que HÁ um token válido

def get_task(task_id):
    return jsonify(task_service.get_task(task_id).to_dict())  # não compara task.user_id com o usuário autenticado

def delete_task(task_id):
    task_service.delete_task(task_id)  # idem
```

**Depois** (helper reutilizável de posse, aplicado a toda rota — recurso do próprio usuário e recurso com dono por FK)
```python
def exigir_proprio_usuario_ou_admin(dono_id):
    """dono_id = id do usuário logado comparado ao dono do recurso.
    Para /usuarios/<id>, dono_id é o próprio id da rota.
    Para um recurso com FK de usuário (ex.: task.user_id), é o valor dessa coluna
    no registro já carregado — nunca um id que vem direto da query string/body."""
    usuario = g.usuario_atual
    if usuario["id"] != dono_id and usuario["tipo"] != "admin":
        raise ForbiddenError("Acesso negado")

# recurso do próprio usuário: dono_id = id da rota
def get_usuario(usuario_id):
    exigir_proprio_usuario_ou_admin(usuario_id)
    return jsonify(usuario_service.buscar(usuario_id).to_dict())

# recurso com dono por chave estrangeira: dono_id = o dono do registro, não o id da rota
def get_task(task_id):
    task = task_service.buscar(task_id)
    exigir_proprio_usuario_ou_admin(task.user_id)
    return jsonify(task.to_dict())

def update_task(task_id):
    task = task_service.buscar(task_id)
    exigir_proprio_usuario_ou_admin(task.user_id)
    # bônus: se o payload tenta reatribuir o dono (ex.: user_id no body), só admin pode
    ...

def delete_task(task_id):
    task = task_service.buscar(task_id)
    exigir_proprio_usuario_ou_admin(task.user_id)
    task_service.remover(task_id)
```
Aplique esse mesmo helper em **toda** rota `GET`/`PUT`/`DELETE` do recurso identificada por id, e em toda rota que lista um sub-recurso de um usuário (`/usuarios/<id>/tasks`, `/usuarios/<id>/pedidos`) — mesmo que o finding original da Fase 2 tenha citado só uma delas como exemplo. Um recurso sem autenticação nenhuma e um recurso autenticado mas sem checagem de dono são o **mesmo anti-pattern (AP-08)** em estágios diferentes; corrigir só o primeiro sem o segundo deixa o finding parcialmente resolvido.

---

## RP-09 — Eliminar estado global mutável

Resolve **AP-09**.

**Antes**
```javascript
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
```
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("loja.db")
    return db_connection
```

**Depois**
```python
# conexão por requisição, usando o contexto do framework
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(settings.DB_PATH)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()
```
```javascript
// cache escopado por request, ou um repositório explícito com TTL — nunca um objeto de módulo mutado por qualquer rota
```

---

## RP-10 — Resolver N+1 com JOIN/eager load

Resolve **AP-10**.

**Antes**
```python
for pedido in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(pedido["id"]))
    for item in itens:
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

**Depois**
```python
cursor.execute("""
    SELECT p.id, p.status, i.produto_id, i.quantidade, pr.nome
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    JOIN produtos pr ON pr.id = i.produto_id
""")
# uma única consulta, agrupada em memória por pedido_id
```
Em ORM: `Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()` em vez de `User.query.get(t.user_id)` dentro do loop.

---

## RP-11 — Deduplicar validação/serialização e remover código morto

Resolve **AP-11**.

**Antes**
```python
# em create_task E update_task, a mesma checagem de título copiada:
if len(title) < 3: return jsonify({'error': '...'}), 400
if len(title) > 200: return jsonify({'error': '...'}), 400
# enquanto utils/helpers.py já define um validador que nunca é chamado
```

**Depois**
```python
# utils/helpers.py
def validate_task_payload(data):
    if not (3 <= len(data.get('title', '')) <= MAX_TITLE_LENGTH):
        raise ValidationError('Título fora do tamanho permitido')
    return data

# routes/task_routes.py — create e update chamam o mesmo validador
data = validate_task_payload(request.get_json())
```
Depois de confirmar que uma função/serviço não é chamada em lugar nenhum (`grep` no projeto), remova-a — código morto não fica "guardado para o futuro".

---

## RP-12 — Migrar APIs deprecated

Resolve **AP-12**.

**Antes**
```javascript
const sqlite3 = require('sqlite3').verbose();       // callback-only
db.get("SELECT ...", [id], (err, row) => { ... });
```

**Depois**
```javascript
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');                 // wrapper com Promises
const db = await open({ filename: ':memory:', driver: sqlite3.Database });
const row = await db.get("SELECT ... WHERE id = ?", [id]);
```
```python
# SQLAlchemy — Query.get() legado em versões recentes
usuario = User.query.get(id)          # antes
usuario = db.session.get(User, id)    # depois
```
Documente a versão da dependência consultada para confirmar a equivalência moderna antes de aplicar a troca.

---

## RP-13 — Nomear magic numbers e melhorar identificadores

Resolve **AP-13**.

**Antes**
```python
if faturamento > 10000: desconto = faturamento * 0.1
```
```javascript
let u = req.body.usr; let cc = req.body.card;
```

**Depois**
```python
# config/business_rules.py
DESCONTO_TIER_1 = (10_000, 0.10)
DESCONTO_TIER_2 = (5_000, 0.05)
DESCONTO_TIER_3 = (1_000, 0.02)
```
```javascript
const username = req.body.usr;
const cardNumber = req.body.card;
```

---

## RP-14 — Centralizar tratamento de erro

Resolve **AP-14**.

**Antes**
```python
try:
    ...
except Exception as e:
    return jsonify({"erro": str(e)}), 500   # vaza stack/detalhe interno
```

**Depois**
```python
# middlewares/error_handler.py
@app.errorhandler(Exception)
def handle_error(e):
    app.logger.exception(e)                  # log interno completo
    code = getattr(e, "code", 500)
    return jsonify({"erro": "Erro interno. Tente novamente."}), code

# nas rotas/services, apenas levante exceções específicas (ValidationError, NotFoundError)
```
```javascript
// middlewares/errorHandler.js
app.use((err, req, res, next) => {
  logger.error(err);
  res.status(err.status || 500).json({ error: 'Erro interno. Tente novamente.' });
});
```

---

Total: 14 transformações, cobrindo todos os 14 anti-patterns do catálogo — acima do mínimo de 8 exigido pelo desafio.
