from src.database.connection import get_db


def _para_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def listar():
    rows = get_db().execute("SELECT * FROM produtos").fetchall()
    return [_para_dict(row) for row in rows]


def buscar_por_id(produto_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return _para_dict(row) if row else None


def buscar_por_ids(produto_ids):
    if not produto_ids:
        return {}
    marcadores = ", ".join("?" for _ in produto_ids)
    rows = get_db().execute(
        "SELECT * FROM produtos WHERE id IN (" + marcadores + ")", list(produto_ids)
    ).fetchall()
    return {row["id"]: _para_dict(row) for row in rows}


def buscar(termo=None, categoria=None, preco_min=None, preco_max=None):
    sql = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        sql += " AND (nome LIKE ? OR descricao LIKE ?)"
        params += ["%" + termo + "%", "%" + termo + "%"]
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    if preco_min:
        sql += " AND preco >= ?"
        params.append(preco_min)
    if preco_max:
        sql += " AND preco <= ?"
        params.append(preco_max)

    rows = get_db().execute(sql, params).fetchall()
    return [_para_dict(row) for row in rows]


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def deletar(produto_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def contar():
    return get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
