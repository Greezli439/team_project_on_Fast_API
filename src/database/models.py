
# from enum import Enum
import enum

from sqlalchemy import Column, Integer, String, Boolean, func, Table, Enum

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import List

Base = declarative_base()


image_m2m_tag = Table(
    "note_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)

    url = Column(String(255), nullable=False)
    title = Column(String(50), nullable=False)
    description = Column(String(150))
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    # comments = relationship(List('comments'))
    username = relationship('User', backref="images")
    tags = relationship("Tag", secondary=image_m2m_tag, backref="images")
    created_at = Column("created_at", DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=func.now(), onupdate=func.now())


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name_tag = Column(String(25), nullable=False, unique=True)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    comment = Column(String(255), nullable=False)
    user_id = Column("user_id", ForeignKey('users.id', ondelete='CASCADE'), default=None)
    username = relationship("User", backref="comments")
    image_id = Column("image_id", ForeignKey("images.id", ondelete="CASCADE"), default=None)
    # image = relationship("Image", backref="comments")
    created_at = Column("created_at", DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=func.now(), onupdate=func.now())

    
class Role(enum.Enum):
    __tablename__ = 'users_roles'
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'

      
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    # images = relationship(List('images'))
    # avatar = relationship('images', backref="users")
    created_at = Column('created_at', DateTime, default=func.now())
    refresh_token = Column(String(255))
    # logout_token = Column(String(255))
    # confirmed = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)
    role = Column('role', Enum(Role), default=Role.user)


# class Role(Base):
#     __tablename__ = 'users_roles'
#     id = Column(Integer, primary_key=True)
#     role_name = Column(String(30), nullable=False, unique=True)

