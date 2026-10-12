from flask import jsonify, request

from services import category_service
from utils.validators import validate_category_payload
from views import category_view


def list_categories():
    categories = category_service.list_categories_with_task_count()
    return jsonify([
        category_view.category_list_item(category, count) for category, count in categories
    ]), 200


def create_category():
    fields = validate_category_payload(request.get_json(silent=True))
    return jsonify(category_service.create_category(fields).to_dict()), 201


def update_category(cat_id):
    fields = validate_category_payload(request.get_json(silent=True), partial=True)
    return jsonify(category_service.update_category(cat_id, fields).to_dict()), 200


def delete_category(cat_id):
    category_service.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
