import logging

from werkzeug.security import generate_password_hash

from src.config.settings import settings
from src.database.connection import abrir_conexao

logger = logging.getLogger(__name__)

PREFIXOS_HASH = ("scrypt:", "pbkdf2:")

SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        preco REAL,
        estoque INTEGER,
        categoria TEXT,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        senha TEXT,
        tipo TEXT DEFAULT 'cliente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        status TEXT DEFAULT 'pendente',
        total REAL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL
    )
    """,
)

PRODUTOS_DEMO = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

# Credenciais de demonstração: gravadas com hash, desligáveis com SEED_DEMO_DATA=false.
USUARIOS_DEMO = [
    ("Admin", "admin@loja.com", "admin123", "admin"),
    ("João Silva", "joao@email.com", "123456", "cliente"),
    ("Maria Santos", "maria@email.com", "senha123", "cliente"),
]


def _criar_tabelas(db):
    for ddl in SCHEMA:
        db.execute(ddl)


def _popular_dados_demo(db):
    if db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] != 0:
        return
    db.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        PRODUTOS_DEMO,
    )
    db.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        [(nome, email, generate_password_hash(senha), tipo) for nome, email, senha, tipo in USUARIOS_DEMO],
    )


def _migrar_senhas_em_texto_plano(db):
    """Bancos criados pela versão legada guardam a senha em claro; converte para hash."""
    linhas = db.execute("SELECT id, senha FROM usuarios").fetchall()
    pendentes = [
        (generate_password_hash(linha["senha"]), linha["id"])
        for linha in linhas
        if linha["senha"] is not None and not linha["senha"].startswith(PREFIXOS_HASH)
    ]
    if pendentes:
        db.executemany("UPDATE usuarios SET senha = ? WHERE id = ?", pendentes)
        logger.warning("%d senha(s) em texto plano convertida(s) para hash", len(pendentes))


def init_db():
    db = abrir_conexao()
    try:
        _criar_tabelas(db)
        _migrar_senhas_em_texto_plano(db)
        if settings.SEED_DEMO_DATA:
            _popular_dados_demo(db)
        db.commit()
    finally:
        db.close()
