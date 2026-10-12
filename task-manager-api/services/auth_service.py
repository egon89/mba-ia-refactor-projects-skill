from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config import settings
from database import db
from models.user import User
from utils.errors import ForbiddenError, UnauthorizedError

TOKEN_SALT = 'auth-token'


def _serializer():
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt=TOKEN_SALT)


def issue_token(user):
    return _serializer().dumps({'user_id': user.id})


def login(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')
    if not user.active:
        raise ForbiddenError('Usuário inativo')
    return user, issue_token(user)


def authenticate(token):
    """Devolve o usuário dono do token ou levanta UnauthorizedError."""
    if not token:
        raise UnauthorizedError('Autenticação necessária')
    try:
        payload = _serializer().loads(token, max_age=settings.TOKEN_TTL_SECONDS)
    except SignatureExpired:
        raise UnauthorizedError('Token expirado')
    except BadSignature:
        raise UnauthorizedError('Token inválido')

    user = db.session.get(User, payload.get('user_id')) if isinstance(payload, dict) else None
    if not user or not user.active:
        raise UnauthorizedError('Token inválido')
    return user
