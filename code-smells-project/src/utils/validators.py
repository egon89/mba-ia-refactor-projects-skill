from src.config import business_rules as regras
from src.utils.errors import ValidationError


def _eh_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _eh_inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _exigir_objeto(dados):
    if not dados or not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")


def validar_produto(dados):
    _exigir_objeto(dados)
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", regras.CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if not isinstance(descricao, str):
        raise ValidationError("Descrição inválida")
    if not _eh_numero(preco):
        raise ValidationError("Preço inválido")
    if not _eh_inteiro(estoque):
        raise ValidationError("Estoque inválido")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < regras.NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > regras.NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in regras.CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(regras.CATEGORIAS_VALIDAS))

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validar_filtro_preco(valor):
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError("Filtro de preço inválido")


def validar_usuario(dados):
    _exigir_objeto(dados)
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not all(isinstance(campo, str) for campo in (nome, email, senha)):
        raise ValidationError("Nome, email e senha são obrigatórios")
    return {"nome": nome, "email": email, "senha": senha}


def validar_login(dados):
    if not isinstance(dados, dict):
        dados = {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha or not isinstance(email, str) or not isinstance(senha, str):
        raise ValidationError("Email e senha são obrigatórios")
    return {"email": email, "senha": senha}


def validar_pedido(dados):
    _exigir_objeto(dados)
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not _eh_inteiro(usuario_id):
        raise ValidationError("Usuario ID inválido")
    if not itens or not isinstance(itens, list):
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    itens_validados = []
    for item in itens:
        if (
            not isinstance(item, dict)
            or not _eh_inteiro(item.get("produto_id"))
            or not _eh_inteiro(item.get("quantidade"))
            or item["quantidade"] <= 0
        ):
            raise ValidationError("Item de pedido inválido")
        itens_validados.append({"produto_id": item["produto_id"], "quantidade": item["quantidade"]})

    return {"usuario_id": usuario_id, "itens": itens_validados}


def validar_status_pedido(dados):
    novo_status = dados.get("status", "") if isinstance(dados, dict) else ""
    if novo_status not in regras.STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    return novo_status
