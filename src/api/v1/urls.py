from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from db.models import User
from schemas import short_urls
from services import my_logger
from services.short_urls import urls_crud
from services.users import current_active_user

logger = my_logger.get_logger(__name__)


router = APIRouter()


@router.get(
    '/user/{user_username}',
    response_model=short_urls.ShortUrlListSchema,
)
async def get_user_urls(
    db: AsyncSession = Depends(get_session),
    user_username: str = Depends(current_active_user),
) -> any:
    user_urls_list = await urls_crud.get_user_urls(
        db=db, username=user_username
    )
    return user_urls_list


@router.get('/urls/{url_id}')
async def get_url(
    *,
    db: AsyncSession = Depends(get_session),
    url_id: int,
) -> any:
    if url_status := await urls_crud.get(db=db, url_id=url_id):
        return ORJSONResponse(url_status)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
    )


@router.get('/urls/{url_id}/status')
async def get_status(
    *,
    db: AsyncSession = Depends(get_session),
    url_id: int,
) -> any:
    url_status = await urls_crud.get_status(db=db, url_id=url_id)
    if not url_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
        )
    return ORJSONResponse(url_status)


@router.post('/urls', status_code=status.HTTP_201_CREATED)
async def create_url(
    *,
    db: AsyncSession = Depends(get_session),
    url_in: short_urls.ShortUrlCreate,
    user: Optional[User] = Depends(current_active_user),
) -> any:
    logger.info('User: %s', user.email)
    url = await urls_crud.create(db=db, obj_in=url_in, user=user)
    return url
