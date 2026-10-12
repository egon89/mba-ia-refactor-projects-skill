from flask import Blueprint

from src.controllers import usuario_controller
from src.middlewares.auth import admin_required, login_required

usuario_bp = Blueprint("usuarios", __name__)

usuario_bp.add_url_rule("/usuarios", view_func=admin_required(usuario_controller.listar_usuarios), methods=["GET"])
usuario_bp.add_url_rule("/usuarios/<int:id>", view_func=login_required(usuario_controller.buscar_usuario), methods=["GET"])
usuario_bp.add_url_rule("/usuarios", view_func=usuario_controller.criar_usuario, methods=["POST"])
usuario_bp.add_url_rule("/login", view_func=usuario_controller.login, methods=["POST"])
