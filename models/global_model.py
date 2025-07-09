import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from config.mysql_database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100))
    email = Column(String(150), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow())
    apikeys = relationship("ApiKey", back_populates="owner")
    proxy = relationship("Proxy", back_populates="owner")


class ApiKey(Base):
    __tablename__ = "apikeys"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    apikey = Column(String(100), unique=True, index=True)
    limit_per_minute = Column(Integer, default=60)  # Limit API calls per minute
    created_at = Column(DateTime, default=datetime.datetime.utcnow())
    user_id = Column(String(36), ForeignKey("users.id"))
    owner = relationship("User", back_populates="apikeys")


class Proxy(Base):
    __tablename__ = "proxy"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    host = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow())
    user_id = Column(String(36), ForeignKey("users.id"))
    owner = relationship("User", back_populates="proxy")
    paths = relationship("ProxyPath", back_populates="proxy")


class ProxyPath(Base):
    __tablename__ = "proxy_paths"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    path = Column(String(255), nullable=False)
    proxy_id = Column(String(36), ForeignKey("proxy.id"))
    proxy = relationship("Proxy", back_populates="paths")
