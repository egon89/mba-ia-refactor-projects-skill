from database import db
from models.category import Category
from models.task import Task
from config import constants
from utils.errors import NotFoundError


def list_categories_with_task_count():
    """Devolve pares (category, task_count) com uma única query de contagem."""
    counts = dict(
        db.session.query(Task.category_id, db.func.count(Task.id)).group_by(Task.category_id).all()
    )
    return [(category, counts.get(category.id, 0)) for category in Category.query.all()]


def get_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')
    return category


def create_category(fields):
    category = Category(
        name=fields['name'],
        description=fields.get('description', ''),
        color=fields.get('color', constants.DEFAULT_CATEGORY_COLOR),
    )
    db.session.add(category)
    db.session.commit()
    return category


def update_category(category_id, fields):
    category = get_category(category_id)
    for name, value in fields.items():
        setattr(category, name, value)
    db.session.commit()
    return category


def delete_category(category_id):
    category = get_category(category_id)
    db.session.delete(category)
    db.session.commit()
