import logging
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _load_secret_key():
    key = os.getenv('SECRET_KEY')
    if key:
        return key
    # Sem segredo configurado: gera um por processo, em vez de cair num valor fixo conhecido.
    logger.warning('SECRET_KEY não definida; usando chave temporária (tokens expiram ao reiniciar).')
    return secrets.token_hex(32)


def _load_list(name):
    return [item.strip() for item in os.getenv(name, '').split(',') if item.strip()]


class Settings:
    SECRET_KEY = _load_secret_key()
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', '5000'))
    CORS_ORIGINS = _load_list('CORS_ORIGINS')
    TOKEN_TTL_SECONDS = int(os.getenv('TOKEN_TTL_SECONDS', str(8 * 60 * 60)))


settings = Settings()
