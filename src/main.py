import uvicorn
from api.v1 import urls
from core.config import app_settings
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from middleware.blocked_ips import BlockedIpsMiddleware
from schemas.users import UserCreate, UserRead
from services import my_logger
from services.users import auth_backend, fastapi_users
from starlette.middleware.base import BaseHTTPMiddleware

logger = my_logger.get_logger(__name__)

app = FastAPI(
    title=app_settings.APP_TITLE,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(urls.router, prefix='/api/v1')

blm = BlockedIpsMiddleware(blocked_ips=app_settings.BLOCKED_IPS)
app.add_middleware(BaseHTTPMiddleware, dispatch=blm)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.PROJECT_HOST,
        port=app_settings.PROJECT_PORT,
    )
