from datetime import datetime
from sqlalchemy import Column, BigInteger, String, JSON, DateTime
from sqlalchemy.orm import declarative_base
from util.datetime_util import now_beijing

Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, index=True)
    business = Column(String(32), nullable=False)
    state = Column(JSON, nullable=False)
    params = Column(JSON, nullable=False)
    dag = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=now_beijing)
    updated_at = Column(DateTime, default=now_beijing, onupdate=now_beijing)

    def __init__(
        self,
        session_id: str,
        user_id: int,
        business: str,
        state: dict = None,
        params: dict = None,
        dag: dict = None
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.business = business
        self.state = state or {}
        self.params = params or {}
        self.dag = dag or {}
