import logging

from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from config import constants
from utils.clock import utcnow
from utils.errors import NotFoundError
from utils.metrics import calculate_percentage

logger = logging.getLogger(__name__)


def list_tasks():
    return Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    return task


def _ensure_references_exist(fields):
    if fields.get('user_id') and not db.session.get(User, fields['user_id']):
        raise NotFoundError('Usuário não encontrado')
    if fields.get('category_id') and not db.session.get(Category, fields['category_id']):
        raise NotFoundError('Categoria não encontrada')


def create_task(fields):
    _ensure_references_exist(fields)
    task = Task(
        description='',
        status=constants.TASK_STATUS_PENDING,
        priority=constants.DEFAULT_PRIORITY,
    )
    for name, value in fields.items():
        setattr(task, name, value)
    db.session.add(task)
    db.session.commit()
    logger.info('Task criada: %s - %s', task.id, task.title)
    return task


def update_task(task_id, fields):
    task = get_task(task_id)
    _ensure_references_exist(fields)
    for name, value in fields.items():
        setattr(task, name, value)
    task.updated_at = utcnow()
    db.session.commit()
    logger.info('Task atualizada: %s', task.id)
    return task


def delete_task(task_id):
    task = get_task(task_id)
    db.session.delete(task)
    db.session.commit()
    logger.info('Task deletada: %s', task_id)


def search_tasks(text=None, status=None, priority=None, user_id=None):
    query = Task.query
    if text:
        query = query.filter(
            db.or_(
                Task.title.like(f'%{text}%'),
                Task.description.like(f'%{text}%')
            )
        )
    if status:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    if user_id is not None:
        query = query.filter(Task.user_id == user_id)
    return query.all()


def list_user_tasks(user_id):
    return Task.query.filter_by(user_id=user_id).all()


def count_by_status():
    rows = db.session.query(Task.status, db.func.count(Task.id)).group_by(Task.status).all()
    counts = {status: 0 for status in constants.TASK_STATUSES}
    for status, count in rows:
        if status in counts:
            counts[status] = count
    return counts


def count_overdue():
    return Task.query.filter(Task.overdue_filter(utcnow())).count()


def get_stats():
    total = Task.query.count()
    by_status = count_by_status()
    stats = {'total': total}
    stats.update(by_status)
    stats['overdue'] = count_overdue()
    stats['completion_rate'] = calculate_percentage(by_status[constants.TASK_STATUS_DONE], total)
    return stats
