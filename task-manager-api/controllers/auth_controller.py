from flask import jsonify, request

from services import auth_service
from utils.validators import validate_login_payload


def login():
    email, password = validate_login_payload(request.get_json(silent=True))
    user, token = auth_service.login(email, password)
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token
    }), 200
