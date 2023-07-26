from abc import ABC, abstractmethod
from typing import Generic, Optional, Type, TypeVar

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import Base
from services import my_logger

logger = my_logger.get_logger(__name__)

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)


class Repository(ABC):
    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDBUrls(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType], request: Type[ModelType]):
        self._model = model
        self._request_model = request

    async def update_counter(
        self, db: AsyncSession, db_obj: ModelType
    ) -> None:
        """Request,
        Update usage_counter in db
        """
        db_obj.usages_count += 1
        await db.commit()
        await db.refresh(db_obj)

    async def get_user_urls(
        self, db: AsyncSession, username: str
    ) -> Optional[ModelType]:
        statement = select(self._model).where(
            self._model.owner.username == username
        )
        urls = await db.scalars(statement=statement)
        return urls

    async def get(self, db: AsyncSession, url_id: int) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.id == url_id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_status(
        self,
        db: AsyncSession,
        url_id: int,
    ) -> Optional[ModelType]:
        url = await self.get(db, url_id)
        try:
            if not url.private:
                return url.usage_count
        except ValueError as e:
            logger.exception('Error %s processing url %r', e, url)

    async def create(
        self, db: AsyncSession, *, obj_in: CreateSchemaType, user: ModelType
    ) -> ModelType:
        logger.info('obj_in: %s', obj_in)
        obj_in_data = jsonable_encoder(obj_in)
        logger.info('obj_in_data: %s', obj_in_data)
        db_obj = self._model(**obj_in_data)
        db_obj.short_url = self.shortener(db_obj.original_url)
        if user:
            db_obj.owner = user.username
        try:
            db.add(db_obj)
            await db.commit()
        except exc.SQLAlchemyError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error
            )
        await db.refresh(db_obj)
        return db_obj
