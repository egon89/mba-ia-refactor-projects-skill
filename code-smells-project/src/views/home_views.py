from flask import Blueprint

from src.controllers import home_controller

home_bp = Blueprint("home", __name__)

home_bp.add_url_rule("/", view_func=home_controller.index, methods=["GET"])
home_bp.add_url_rule("/health", view_func=home_controller.health_check, methods=["GET"])
