import sqlite3

from flask import g

from src.config.settings import settings


def abrir_conexao():
    conexao = sqlite3.connect(settings.DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def get_db():
    """Conexão escopada à requisição; fechada no teardown."""
    if "db" not in g:
        g.db = abrir_conexao()
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        # fechar sem commit descarta qualquer escrita pendente de uma requisição que falhou
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
