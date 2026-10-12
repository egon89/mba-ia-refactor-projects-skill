from flask import jsonify

from src.config.business_rules import API_VERSION
from src.config.settings import settings
from src.services import health_service


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": API_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health"
        }
    })


def health_check():
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": health_service.contagens(),
        "versao": API_VERSION,
        "ambiente": settings.ENVIRONMENT
    }), 200
