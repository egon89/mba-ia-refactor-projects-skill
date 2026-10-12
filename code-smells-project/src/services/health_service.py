from src.models import pedido_model, produto_model, usuario_model


def contagens():
    return {
        "produtos": produto_model.contar(),
        "usuarios": usuario_model.contar(),
        "pedidos": pedido_model.contar(),
    }
