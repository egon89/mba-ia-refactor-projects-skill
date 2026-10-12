from src.database.connection import get_db


def _para_dict(row):
    # a coluna `senha` (hash) nunca entra no serializador público
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def listar():
    rows = get_db().execute("SELECT * FROM usuarios").fetchall()
    return [_para_dict(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _para_dict(row) if row else None


def listar_credenciais_por_email(email):
    """Uso exclusivo da autenticação: devolve o hash da senha junto com o usuário."""
    rows = get_db().execute(
        "SELECT id, nome, email, tipo, senha FROM usuarios WHERE email = ? ORDER BY id", (email,)
    ).fetchall()
    return [
        {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "senha_hash": row["senha"],
        }
        for row in rows
    ]


def criar(nome, email, senha_hash, tipo):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def contar():
    return get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
