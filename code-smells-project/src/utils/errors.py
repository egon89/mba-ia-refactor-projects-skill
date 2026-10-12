class AppError(Exception):
    status_code = 500

    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


class ValidationError(AppError):
    status_code = 400


class BusinessRuleError(AppError):
    status_code = 400


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class NotFoundError(AppError):
    status_code = 404


class EstoqueInsuficienteError(Exception):
    """Levantada pelo model quando a baixa de estoque não encontra saldo."""

    def __init__(self, produto_id):
        super().__init__(produto_id)
        self.produto_id = produto_id
