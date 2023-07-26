import uuid

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from core.config import app_settings
from db.db import AsyncSession, get_session
from db.models import User
from services import my_logger

logger = my_logger.get_logger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = app_settings.RESET_PASSWORD_SECRET_KEY
    verification_token_secret = app_settings.VERIFICATION_SECRET_KEY


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=app_settings.JWT_SECRET_KEY, lifetime_seconds=3600
    )


async def get_enabled_backend(request: Request) -> list[AuthenticationBackend]:
    """Return the enabled dependencies following custom logic."""
    if request.url.path == '/protected-route-only-jwt':
        return [jwt_backend]
    else:
        return [cookie_backend, jwt_backend]


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)) -> UserManager:
    yield UserManager(user_db)


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=app_settings.BEARER_TRANSPORT,
    get_strategy=get_jwt_strategy,
)

jwt_backend = AuthenticationBackend(
    name='jwt',
    transport=app_settings.BEARER_TRANSPORT,
    get_strategy=get_jwt_strategy,
)

cookie_backend = AuthenticationBackend(
    name='jwt',
    transport=app_settings.COOKIE_TRANSPORT,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(
    active=True, get_enabled_backends=get_enabled_backend
)
