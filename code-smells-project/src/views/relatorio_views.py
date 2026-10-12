from flask import Blueprint

from src.controllers import relatorio_controller
from src.middlewares.auth import admin_required

relatorio_bp = Blueprint("relatorios", __name__)

relatorio_bp.add_url_rule("/relatorios/vendas", view_func=admin_required(relatorio_controller.relatorio_vendas), methods=["GET"])
