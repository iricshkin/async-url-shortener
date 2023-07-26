import os
from logging import config as logging_config

from fastapi_users.authentication import BearerTransport, CookieTransport
from pydantic import BaseSettings, PostgresDsn

from .logger import LOGGING

logging_config.dictConfig(LOGGING)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = 'shorty.log'


class AppSettings(BaseSettings):
    APP_TITLE: str = 'URLShortener'
    DATABASE_DSN: PostgresDsn
    PROJECT_HOST: str
    PROJECT_PORT: int
    RESET_PASSWORD_SECRET_KEY: str
    VERIFICATION_SECRET_KEY: str
    JWT_SECRET_KEY: str
    BEARER_TRANSPORT: str = BearerTransport(tokenUrl='auth/jwt/login')
    COOKIE_TRANSPORT: str = CookieTransport(cookie_max_age=3600)
    BLOCKED_IPS: list[str] = []

    class Config:
        env_file = '.env'


app_settings = AppSettings()
