from functools import wraps

from flask import g, request

from services import auth_service
from utils.errors import ForbiddenError, UnauthorizedError

BEARER_PREFIX = 'Bearer '


def _bearer_token():
    header = request.headers.get('Authorization', '')
    if not header.startswith(BEARER_PREFIX):
        return None
    return header[len(BEARER_PREFIX):].strip()


def authenticate_request():
    """before_request de blueprint: exige token válido em todas as rotas dele."""
    if request.method == 'OPTIONS':
        return
    g.current_user = auth_service.authenticate(_bearer_token())


def current_user_or_none():
    """Para rotas públicas que mudam de comportamento quando há um usuário autenticado."""
    token = _bearer_token()
    if not token:
        return None
    try:
        return auth_service.authenticate(token)
    except UnauthorizedError:
        return None


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        authenticate_request()
        return fn(*args, **kwargs)
    return wrapper


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        authenticate_request()
        if not g.current_user.is_admin():
            raise ForbiddenError('Acesso restrito a administradores')
        return fn(*args, **kwargs)
    return wrapper


def ensure_self_or_admin(user_id):
    if g.current_user.id != user_id and not g.current_user.is_admin():
        raise ForbiddenError('Acesso negado')
