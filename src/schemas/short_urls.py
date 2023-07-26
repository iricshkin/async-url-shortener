from datetime import datetime

from pydantic import BaseModel, HttpUrl, validator


class ShortUrlBase(BaseModel):
    title: str
    original_url: HttpUrl

    @validator('original_url')
    def url_startswith_http(cls, v):
        if v.startswith(('https://', 'http://')):
            return v
        raise ValueError('url mast starts with https:// or http://')


class ShortUrlCreate(ShortUrlBase):
    created_at: datetime


class ShortUrlInDBBase(ShortUrlBase):
    id: int
    title: str | None
    original_url: HttpUrl | None
    private: bool = False
    short_url: HttpUrl | None
    usage_count: int = 0
    created_at: datetime | None
    owner: str | None

    class Config:
        orm_mode = True


class ShortUrlListSchema(BaseModel):
    __root__: list[ShortUrlInDBBase]
