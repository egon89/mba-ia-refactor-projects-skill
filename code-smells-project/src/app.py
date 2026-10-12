import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import settings
from src.database import connection
from src.database.schema import init_db
from src.middlewares.error_handler import register_error_handlers
from src.views import BLUEPRINTS

logger = logging.getLogger(__name__)


def create_app():
    logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app, origins=settings.CORS_ORIGINS)

    if settings.SECRET_KEY_EFEMERA:
        logger.warning("SECRET_KEY não definida: usando chave aleatória; tokens expiram a cada restart")

    connection.init_app(app)
    init_db()
    register_error_handlers(app)
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    return app
