from src.models import pedido_model, produto_model
from src.services import notification_service
from src.utils.errors import BusinessRuleError, EstoqueInsuficienteError


def criar(usuario_id, itens):
    produtos = produto_model.buscar_por_ids({item["produto_id"] for item in itens})

    total = 0
    itens_precificados = []
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            raise BusinessRuleError("Produto " + str(item["produto_id"]) + " não encontrado")
        if produto["estoque"] < item["quantidade"]:
            raise BusinessRuleError("Estoque insuficiente para " + produto["nome"])
        total = total + (produto["preco"] * item["quantidade"])
        itens_precificados.append({**item, "preco_unitario": produto["preco"]})

    try:
        pedido_id = pedido_model.criar(usuario_id, itens_precificados, total)
    except EstoqueInsuficienteError as erro:
        # o saldo mudou entre a leitura e a baixa (ou o mesmo produto veio repetido no pedido)
        raise BusinessRuleError("Estoque insuficiente para " + produtos[erro.produto_id]["nome"])

    notification_service.notificar_pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def listar_todos():
    return pedido_model.listar()


def listar_por_usuario(usuario_id):
    return pedido_model.listar(usuario_id)


def atualizar_status(pedido_id, novo_status):
    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.notificar_mudanca_status(pedido_id, novo_status)
