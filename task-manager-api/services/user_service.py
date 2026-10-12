import logging

from database import db
from models.task import Task
from models.user import User
from config import constants
from utils.errors import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


def list_users_with_task_count():
    """Devolve pares (user, task_count) com uma única query de contagem."""
    counts = dict(
        db.session.query(Task.user_id, db.func.count(Task.id)).group_by(Task.user_id).all()
    )
    return [(user, counts.get(user.id, 0)) for user in User.query.all()]


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return user


def _ensure_email_available(email, ignore_user_id=None):
    existing = User.query.filter_by(email=email).first()
    if existing and existing.id != ignore_user_id:
        raise ConflictError('Email já cadastrado')


def create_user(fields):
    _ensure_email_available(fields['email'])
    user = User(
        name=fields['name'],
        email=fields['email'],
        role=fields.get('role', constants.ROLE_USER),
    )
    user.set_password(fields['password'])
    db.session.add(user)
    db.session.commit()
    logger.info('Usuário criado: %s', user.id)
    return user


def update_user(user_id, fields):
    user = get_user(user_id)
    if 'email' in fields:
        _ensure_email_available(fields['email'], ignore_user_id=user_id)
    for name, value in fields.items():
        if name == 'password':
            user.set_password(value)
        else:
            setattr(user, name, value)
    db.session.commit()
    return user


def delete_user(user_id):
    user = get_user(user_id)
    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    logger.info('Usuário deletado: %s', user_id)
