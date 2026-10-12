from flask import Blueprint

from controllers import user_controller
from middlewares.auth import require_admin, require_auth

user_bp = Blueprint('users', __name__)

# POST /users (cadastro) é a única rota pública deste blueprint.
user_bp.add_url_rule('/users', view_func=user_controller.create_user, methods=['POST'])
user_bp.add_url_rule('/users', view_func=require_auth(user_controller.list_users), methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=require_auth(user_controller.get_user), methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=require_auth(user_controller.update_user), methods=['PUT'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=require_admin(user_controller.delete_user), methods=['DELETE'])
user_bp.add_url_rule('/users/<int:user_id>/tasks', view_func=require_auth(user_controller.list_user_tasks), methods=['GET'])
