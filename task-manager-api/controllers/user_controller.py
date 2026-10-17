from flask import g, jsonify, request

from config.constants import ROLE_USER
from middlewares.auth import current_user_or_none, ensure_self_or_admin
from services import task_service, user_service
from utils.errors import ForbiddenError
from utils.validators import validate_user_payload
from views import task_view, user_view

ADMIN_ONLY_FIELDS = ('role', 'active')


def list_users():
    users = user_service.list_users_with_task_count()
    return jsonify([user_view.user_list_item(user, count) for user, count in users]), 200


def get_user(user_id):
    ensure_self_or_admin(user_id)
    user = user_service.get_user(user_id)
    return jsonify(user_view.user_detail(user, task_service.list_user_tasks(user_id))), 200


def create_user():
    fields = validate_user_payload(request.get_json(silent=True))
    # Cadastro é público, mas só um admin autenticado cria conta com papel elevado.
    if fields.get('role', ROLE_USER) != ROLE_USER:
        requester = current_user_or_none()
        if not requester or not requester.is_admin():
            raise ForbiddenError('Apenas administradores podem definir o role')
    return jsonify(user_service.create_user(fields).to_dict()), 201


def update_user(user_id):
    ensure_self_or_admin(user_id)
    fields = validate_user_payload(request.get_json(silent=True), partial=True)
    if not g.current_user.is_admin() and any(name in fields for name in ADMIN_ONLY_FIELDS):
        raise ForbiddenError('Apenas administradores podem alterar role ou active')
    return jsonify(user_service.update_user(user_id, fields).to_dict()), 200


def delete_user(user_id):
    user_service.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def list_user_tasks(user_id):
    ensure_self_or_admin(user_id)
    user_service.get_user(user_id)
    tasks = task_service.list_user_tasks(user_id)
    return jsonify([task_view.user_task_item(task) for task in tasks]), 200
