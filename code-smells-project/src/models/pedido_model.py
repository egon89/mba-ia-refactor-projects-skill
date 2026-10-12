from src.config.business_rules import STATUS_APROVADO, STATUS_CANCELADO, STATUS_PENDENTE
from src.database.connection import get_db
from src.utils.errors import EstoqueInsuficienteError


def criar(usuario_id, itens, total):
    """Grava pedido, itens e baixa de estoque em uma única transação.

    Cada item traz `produto_id`, `quantidade` e `preco_unitario`.
    """
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PENDENTE, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            baixa = db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (item["quantidade"], item["produto_id"], item["quantidade"]),
            )
            if baixa.rowcount == 0:
                raise EstoqueInsuficienteError(item["produto_id"])

        db.commit()
    except Exception:
        db.rollback()
        raise
    return pedido_id


def listar(usuario_id=None):
    sql = """
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
               pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
    """
    params = []
    if usuario_id is not None:
        sql += " WHERE p.usuario_id = ?"
        params.append(usuario_id)
    sql += " ORDER BY p.id, i.id"

    pedidos = {}
    for row in get_db().execute(sql, params):
        pedido = pedidos.setdefault(
            row["id"],
            {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            },
        )
        if row["item_id"] is not None:
            pedido["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] if row["produto_nome"] is not None else "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return list(pedidos.values())


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()


def resumo_vendas():
    row = get_db().execute(
        """
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(status = ?), 0) AS pendentes,
               COALESCE(SUM(status = ?), 0) AS aprovados,
               COALESCE(SUM(status = ?), 0) AS cancelados
        FROM pedidos
        """,
        (STATUS_PENDENTE, STATUS_APROVADO, STATUS_CANCELADO),
    ).fetchone()
    return dict(row)


def contar():
    return get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
