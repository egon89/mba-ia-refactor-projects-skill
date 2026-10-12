import logging

from itsdangerous import BadSignature, URLSafeTimedSerializer
from werkzeug.security import check_password_hash

from src.config.settings import settings
from src.models import usuario_model
from src.utils.errors import UnauthorizedError

logger = logging.getLogger(__name__)

_SALT = "auth-token"


def _serializer():
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt=_SALT)


def gerar_token(usuario):
    return _serializer().dumps({"id": usuario["id"], "tipo": usuario["tipo"]})


def validar_token(token):
    try:
        return _serializer().loads(token, max_age=settings.TOKEN_TTL_SECONDS)
    except BadSignature:  # inclui SignatureExpired
        raise UnauthorizedError("Token inválido ou expirado")


def autenticar(email, senha):
    """Devolve (usuario, token) ou levanta UnauthorizedError."""
    for candidato in usuario_model.listar_credenciais_por_email(email):
        if candidato["senha_hash"] and check_password_hash(candidato["senha_hash"], senha):
            usuario = {
                "id": candidato["id"],
                "nome": candidato["nome"],
                "email": candidato["email"],
                "tipo": candidato["tipo"],
            }
            logger.info("Login bem-sucedido: usuario_id=%s", usuario["id"])
            return usuario, gerar_token(usuario)

    logger.info("Login falhou")
    raise UnauthorizedError("Email ou senha inválidos")
