from flask import Blueprint

from src.controllers import produto_controller
from src.middlewares.auth import admin_required

produto_bp = Blueprint("produtos", __name__)

produto_bp.add_url_rule("/produtos", view_func=produto_controller.listar_produtos, methods=["GET"])
produto_bp.add_url_rule("/produtos/busca", view_func=produto_controller.buscar_produtos, methods=["GET"])
produto_bp.add_url_rule("/produtos/<int:id>", view_func=produto_controller.buscar_produto, methods=["GET"])
produto_bp.add_url_rule("/produtos", view_func=admin_required(produto_controller.criar_produto), methods=["POST"])
produto_bp.add_url_rule("/produtos/<int:id>", view_func=admin_required(produto_controller.atualizar_produto), methods=["PUT"])
produto_bp.add_url_rule("/produtos/<int:id>", view_func=admin_required(produto_controller.deletar_produto), methods=["DELETE"])
