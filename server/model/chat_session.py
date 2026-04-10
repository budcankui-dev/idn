from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import declarative_base
from util.datetime_util import now_beijing

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = 'chat_session'
    __table_args__ = (UniqueConstraint('session_id', name='unique_session_id'),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False)
    user_id = Column(BigInteger, nullable=True)  # 外键关联 user.id，为空表示未登录用户
    business = Column(String(32), nullable=False)
    prompt = Column(Text, nullable=True)
    history = Column(JSON, nullable=True)
    state = Column(JSON, nullable=False)
    params = Column(JSON, nullable=False)
    dag = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=now_beijing)
    updated_at = Column(DateTime, default=now_beijing, onupdate=now_beijing)

    def __init__(
        self,
        session_id: str,
        business: str,
        user_id: Optional[int] = None,
        prompt: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        state: Dict = None,
        params: Dict = None,
        dag: Dict = None
    ):
        if not isinstance(state, dict):
            raise ValueError("state must be a dict")
        if not isinstance(params, dict):
            raise ValueError("params must be a dict")
        if not isinstance(dag, dict):
            raise ValueError("dag must be a dict")

        self.session_id = session_id
        self.user_id = user_id
        self.business = business
        self.prompt = prompt
        self.history = history or []
        self.state = state
        self.params = params
        self.dag = dag