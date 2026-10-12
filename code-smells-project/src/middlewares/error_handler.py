import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from src.utils.errors import AppError

logger = logging.getLogger(__name__)


def _resposta(mensagem, status):
    return jsonify({"erro": mensagem, "sucesso": False}), status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def tratar_erro_da_aplicacao(erro):
        return _resposta(erro.mensagem, erro.status_code)

    @app.errorhandler(HTTPException)
    def tratar_erro_http(erro):
        return _resposta(erro.description, erro.code)

    @app.errorhandler(Exception)
    def tratar_erro_inesperado(erro):
        # o detalhe fica só no log; o cliente recebe uma mensagem genérica
        logger.exception("Erro não tratado")
        return _resposta("Erro interno do servidor", 500)
