import os
import secrets


def _env_bool(nome, padrao="false"):
    return os.getenv(nome, padrao).strip().lower() in ("1", "true", "yes")


def _env_lista(nome, padrao):
    return [item.strip() for item in os.getenv(nome, padrao).split(",") if item.strip()]


class Settings:
    def __init__(self):
        # Sem SECRET_KEY no ambiente, gera uma chave aleatória por processo:
        # a aplicação sobe, mas os tokens emitidos não sobrevivem a um restart.
        self.SECRET_KEY_EFEMERA = not os.getenv("SECRET_KEY")
        self.SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
        self.DEBUG = _env_bool("DEBUG")
        self.HOST = os.getenv("HOST", "127.0.0.1")
        self.PORT = int(os.getenv("PORT", "5000"))
        self.DB_PATH = os.getenv("DB_PATH", "loja.db")
        self.CORS_ORIGINS = _env_lista("CORS_ORIGINS", "http://localhost:3000")
        self.TOKEN_TTL_SECONDS = int(os.getenv("TOKEN_TTL_SECONDS", "28800"))
        self.ENVIRONMENT = os.getenv("APP_ENV", "producao")
        self.SEED_DEMO_DATA = _env_bool("SEED_DEMO_DATA", "true")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


settings = Settings()
