from flask import jsonify

from src.middlewares.auth import exigir_proprio_usuario_ou_admin
from src.services import auth_service, usuario_service
from src.utils import validators
from src.utils.http import corpo_json


def listar_usuarios():
    usuarios = usuario_service.listar()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(id):
    exigir_proprio_usuario_ou_admin(id)
    usuario = usuario_service.obter(id)
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    dados = validators.validar_usuario(corpo_json())
    usuario_id = usuario_service.criar(dados)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    credenciais = validators.validar_login(corpo_json())
    usuario, token = auth_service.autenticar(credenciais["email"], credenciais["senha"])
    return jsonify({"dados": usuario, "token": token, "sucesso": True, "mensagem": "Login OK"}), 200
