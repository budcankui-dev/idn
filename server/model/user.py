from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Enum, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from util.datetime_util import now_beijing

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(128), nullable=True)
    role = Column(Enum('normal', 'admin', name='user_role'), default='normal')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now_beijing)
    updated_at = Column(DateTime, default=now_beijing, onupdate=now_beijing)

    def __init__(
        self,
        username: str,
        password_hash: str,
        email: str = None,
        role: str = 'normal',
        is_active: bool = True
    ):
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role
        self.is_active = is_active
