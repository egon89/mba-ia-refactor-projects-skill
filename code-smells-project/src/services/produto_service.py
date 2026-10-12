import logging

from src.models import produto_model
from src.utils.errors import NotFoundError

logger = logging.getLogger(__name__)


def listar():
    return produto_model.listar()


def obter(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado")
    return produto


def buscar(termo, categoria, preco_min, preco_max):
    return produto_model.buscar(termo, categoria, preco_min, preco_max)


def criar(dados):
    produto_id = produto_model.criar(
        dados["nome"], dados["descricao"], dados["preco"], dados["estoque"], dados["categoria"]
    )
    logger.info("Produto criado com ID: %s", produto_id)
    return produto_id


def atualizar(produto_id, dados):
    produto_model.atualizar(
        produto_id, dados["nome"], dados["descricao"], dados["preco"], dados["estoque"], dados["categoria"]
    )


def deletar(produto_id):
    obter(produto_id)
    produto_model.deletar(produto_id)
    logger.info("Produto %s deletado", produto_id)
