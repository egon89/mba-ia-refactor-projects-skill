from flask import g, jsonify, request

from middlewares.auth import ensure_self_or_admin
from services import task_service
from utils.errors import ForbiddenError
from utils.validators import parse_int_param, validate_task_payload
from views import task_view


def list_tasks():
    return jsonify([task_view.task_list_item(task) for task in task_service.list_tasks()]), 200


def get_task(task_id):
    task = task_service.get_task(task_id)
    ensure_self_or_admin(task.user_id)
    return jsonify(task_view.task_detail(task)), 200


def create_task():
    fields = validate_task_payload(request.get_json(silent=True))
    return jsonify(task_service.create_task(fields).to_dict()), 201


def update_task(task_id):
    task = task_service.get_task(task_id)
    ensure_self_or_admin(task.user_id)
    fields = validate_task_payload(request.get_json(silent=True), partial=True)
    if not g.current_user.is_admin() and 'user_id' in fields and fields['user_id'] != g.current_user.id:
        raise ForbiddenError('Apenas administradores podem reatribuir a task para outro usuário')
    return jsonify(task_service.update_task(task_id, fields).to_dict()), 200


def delete_task(task_id):
    task = task_service.get_task(task_id)
    ensure_self_or_admin(task.user_id)
    task_service.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')
    tasks = task_service.search_tasks(
        text=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=parse_int_param(priority, 'priority') if priority else None,
        user_id=parse_int_param(user_id, 'user_id') if user_id else None,
    )
    return jsonify([task.to_dict() for task in tasks]), 200


def task_stats():
    return jsonify(task_service.get_stats()), 200
