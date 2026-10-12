from flask import request


def corpo_json():
    """Corpo JSON da requisição, ou None quando ausente/malformado (a validação decide o erro)."""
    return request.get_json(silent=True)
