from flask import g, jsonify

from src.services import admin_service


def reset_database():
    admin_service.resetar_banco(g.usuario_atual["id"])
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
