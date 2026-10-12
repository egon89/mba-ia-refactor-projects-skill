from flask import jsonify, request

from src.services import produto_service
from src.utils import validators
from src.utils.http import corpo_json


def listar_produtos():
    produtos = produto_service.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_service.obter(id)
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    dados = validators.validar_produto(corpo_json())
    produto_id = produto_service.criar(dados)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    produto_service.obter(id)
    dados = validators.validar_produto(corpo_json())
    produto_service.atualizar(id, dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    produto_service.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = validators.validar_filtro_preco(request.args.get("preco_min", None))
    preco_max = validators.validar_filtro_preco(request.args.get("preco_max", None))

    resultados = produto_service.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
