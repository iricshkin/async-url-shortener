from db.models import ShortUrl
from schemas.short_urls import ShortUrlCreate, ShortUrlListSchema

from .base import RepositoryDBUrls


class RepositoryURL(RepositoryDBUrls[ShortUrl, ShortUrlCreate]):
    pass


urls_crud = RepositoryURL(ShortUrl, ShortUrlListSchema)
