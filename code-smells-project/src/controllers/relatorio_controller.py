from flask import jsonify

from src.services import relatorio_service


def relatorio_vendas():
    relatorio = relatorio_service.vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200
