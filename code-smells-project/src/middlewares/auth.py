from functools import wraps

from flask import g, request

from src.config.business_rules import TIPO_ADMIN
from src.services import auth_service
from src.utils.errors import ForbiddenError, UnauthorizedError

_PREFIXO_BEARER = "Bearer "


def _autenticar_requisicao():
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.startswith(_PREFIXO_BEARER):
        raise UnauthorizedError("Autenticação necessária")
    g.usuario_atual = auth_service.validar_token(cabecalho[len(_PREFIXO_BEARER):])
    return g.usuario_atual


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        _autenticar_requisicao()
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        usuario = _autenticar_requisicao()
        if usuario["tipo"] != TIPO_ADMIN:
            raise ForbiddenError("Acesso negado")
        return fn(*args, **kwargs)

    return wrapper


def exigir_proprio_usuario_ou_admin(usuario_id):
    """Para rotas que expõem dado de um usuário específico."""
    usuario = g.usuario_atual
    if usuario["tipo"] != TIPO_ADMIN and usuario["id"] != usuario_id:
        raise ForbiddenError("Acesso negado")
