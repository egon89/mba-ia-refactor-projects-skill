import logging

from werkzeug.security import generate_password_hash

from src.config.business_rules import TIPO_CLIENTE
from src.models import usuario_model
from src.utils.errors import NotFoundError

logger = logging.getLogger(__name__)


def listar():
    return usuario_model.listar()


def obter(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return usuario


def criar(dados):
    usuario_id = usuario_model.criar(
        dados["nome"], dados["email"], generate_password_hash(dados["senha"]), TIPO_CLIENTE
    )
    logger.info("Usuário criado: id=%s", usuario_id)
    return usuario_id
