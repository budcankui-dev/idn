from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.orm import declarative_base
from util.datetime_util import now_beijing

Base = declarative_base()


class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    title = Column(String(128), default='')
    created_at = Column(DateTime, default=now_beijing)
    updated_at = Column(DateTime, default=now_beijing, onupdate=now_beijing)

    def __init__(self, session_id: str, user_id: int, title: str = ''):
        self.session_id = session_id
        self.user_id = user_id
        self.title = title
