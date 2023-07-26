from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from db.db import Base


class ShortUrl(Base):
    __tablename__ = 'short_urls'
    id = Column(Integer, primary_key=True)
    title = Column(
        String(20),
        unique=True,
        comment='Short url name',
    )
    private = Column(
        Boolean,
        comment='Short url visibility',
    )
    original_url = Column(
        URLType,
        nullable=False,
        comment='Original url',
    )
    short_url = Column(
        URLType,
        nullable=False,
        comment='Short url',
    )
    usage_count = Column(
        Integer,
        comment='Url usage activity analysis',
    )
    created_at = Column(
        DateTime,
        index=True,
        default=datetime.utcnow,
        comment='Short urlcreation time',
    )
    owner = relationship(
        'User',
        backref='shorturls',
        cascade="all, delete",
        comment='Short url owner',
    )


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = 'user'
    username = Column(
        String(20),
        unique=True,
        comment='Enter username',
    )
    urls = Column(
        Integer,
        ForeignKey('short_urls.id', ondelete='CASCADE'),
        comment='List of user urls',
    )
