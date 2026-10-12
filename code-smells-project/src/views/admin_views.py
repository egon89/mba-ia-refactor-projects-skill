from flask import Blueprint

from src.controllers import admin_controller
from src.middlewares.auth import admin_required

admin_bp = Blueprint("admin", __name__)

admin_bp.add_url_rule("/admin/reset-db", view_func=admin_required(admin_controller.reset_database), methods=["POST"])
