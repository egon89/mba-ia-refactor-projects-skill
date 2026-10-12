from flask import Blueprint

from src.controllers import pedido_controller
from src.middlewares.auth import admin_required, login_required

pedido_bp = Blueprint("pedidos", __name__)

pedido_bp.add_url_rule("/pedidos", view_func=login_required(pedido_controller.criar_pedido), methods=["POST"])
pedido_bp.add_url_rule("/pedidos", view_func=admin_required(pedido_controller.listar_todos_pedidos), methods=["GET"])
pedido_bp.add_url_rule("/pedidos/usuario/<int:usuario_id>", view_func=login_required(pedido_controller.listar_pedidos_usuario), methods=["GET"])
pedido_bp.add_url_rule("/pedidos/<int:pedido_id>/status", view_func=admin_required(pedido_controller.atualizar_status_pedido), methods=["PUT"])
