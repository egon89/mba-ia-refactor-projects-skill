import logging

from src.models import manutencao_model

logger = logging.getLogger(__name__)


def resetar_banco(usuario_id):
    manutencao_model.apagar_todos_os_dados()
    logger.warning("BANCO DE DADOS RESETADO por usuario_id=%s", usuario_id)
