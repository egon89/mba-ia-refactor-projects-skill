from flask import jsonify

from src.middlewares.auth import exigir_proprio_usuario_ou_admin
from src.services import pedido_service
from src.utils import validators
from src.utils.http import corpo_json


def criar_pedido():
    dados = validators.validar_pedido(corpo_json())
    exigir_proprio_usuario_ou_admin(dados["usuario_id"])
    resultado = pedido_service.criar(dados["usuario_id"], dados["itens"])
    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso"
    }), 201


def listar_pedidos_usuario(usuario_id):
    exigir_proprio_usuario_ou_admin(usuario_id)
    pedidos = pedido_service.listar_por_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = pedido_service.listar_todos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    novo_status = validators.validar_status_pedido(corpo_json())
    pedido_service.atualizar_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
