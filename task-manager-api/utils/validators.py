import re
from datetime import datetime

from config import constants
from utils.errors import ValidationError


def require_json_object(data):
    if not data or not isinstance(data, dict):
        raise ValidationError('Dados inválidos')
    return data


def parse_int_param(value, name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(f'Parâmetro {name} inválido')


def _validate_title(title):
    if not isinstance(title, str):
        raise ValidationError('Título inválido')
    if len(title) < constants.MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > constants.MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def _validate_status(status):
    if status not in constants.TASK_STATUSES:
        raise ValidationError('Status inválido')
    return status


def _validate_priority(priority):
    if isinstance(priority, bool) or not isinstance(priority, int):
        raise ValidationError('Prioridade inválida')
    if priority < constants.MIN_PRIORITY or priority > constants.MAX_PRIORITY:
        raise ValidationError(
            f'Prioridade deve ser entre {constants.MIN_PRIORITY} e {constants.MAX_PRIORITY}'
        )
    return priority


def _validate_reference_id(value, label):
    if not value:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f'{label} inválido')
    return value


def _parse_due_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, constants.DUE_DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError('Formato de data inválido. Use YYYY-MM-DD')


def _normalize_tags(tags):
    if not tags:
        return None
    if isinstance(tags, list):
        if not all(isinstance(tag, str) for tag in tags):
            raise ValidationError('Tags inválidas')
        return ','.join(tags)
    if not isinstance(tags, str):
        raise ValidationError('Tags inválidas')
    return tags


def validate_task_payload(data, partial=False):
    """Valida o payload de criação (partial=False) ou atualização (partial=True) de task.

    Devolve só os campos presentes, já normalizados. A existência de user_id e
    category_id é checada pelo service, que tem acesso aos models.
    """
    require_json_object(data)
    fields = {}

    if not partial and not data.get('title'):
        raise ValidationError('Título é obrigatório')
    if 'title' in data:
        fields['title'] = _validate_title(data['title'])

    if 'description' in data:
        fields['description'] = data['description']
    if 'status' in data:
        fields['status'] = _validate_status(data['status'])
    if 'priority' in data:
        fields['priority'] = _validate_priority(data['priority'])
    if 'user_id' in data:
        fields['user_id'] = _validate_reference_id(data['user_id'], 'Usuário')
    if 'category_id' in data:
        fields['category_id'] = _validate_reference_id(data['category_id'], 'Categoria')
    if 'due_date' in data:
        fields['due_date'] = _parse_due_date(data['due_date'])
    if 'tags' in data:
        fields['tags'] = _normalize_tags(data['tags'])

    return fields


def _validate_name(name):
    if not name:
        raise ValidationError('Nome é obrigatório')
    if not isinstance(name, str):
        raise ValidationError('Nome inválido')
    return name


def _validate_email(email):
    if not isinstance(email, str) or not re.match(constants.EMAIL_PATTERN, email):
        raise ValidationError('Email inválido')
    return email


def _validate_password(password, too_short_message):
    if not isinstance(password, str):
        raise ValidationError('Senha inválida')
    if len(password) < constants.MIN_PASSWORD_LENGTH:
        raise ValidationError(too_short_message)
    return password


def _validate_role(role):
    if role not in constants.USER_ROLES:
        raise ValidationError('Role inválido')
    return role


def validate_user_payload(data, partial=False):
    require_json_object(data)
    fields = {}

    if not partial:
        if not data.get('name'):
            raise ValidationError('Nome é obrigatório')
        if not data.get('email'):
            raise ValidationError('Email é obrigatório')
        if not data.get('password'):
            raise ValidationError('Senha é obrigatória')

    if 'name' in data:
        fields['name'] = _validate_name(data['name'])
    if 'email' in data:
        fields['email'] = _validate_email(data['email'])
    if 'password' in data:
        too_short = 'Senha muito curta' if partial else (
            f'Senha deve ter no mínimo {constants.MIN_PASSWORD_LENGTH} caracteres'
        )
        fields['password'] = _validate_password(data['password'], too_short)
    if 'role' in data:
        fields['role'] = _validate_role(data['role'])
    if partial and 'active' in data:
        if not isinstance(data['active'], bool):
            raise ValidationError('Campo active inválido')
        fields['active'] = data['active']

    return fields


def validate_category_payload(data, partial=False):
    require_json_object(data)
    fields = {}

    if not partial and not data.get('name'):
        raise ValidationError('Nome é obrigatório')
    if 'name' in data:
        fields['name'] = _validate_name(data['name'])
    if 'description' in data:
        fields['description'] = data['description']
    if 'color' in data:
        fields['color'] = data['color']

    return fields


def validate_login_payload(data):
    require_json_object(data)
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')
    if not isinstance(email, str) or not isinstance(password, str):
        raise ValidationError('Email e senha são obrigatórios')
    return email, password
