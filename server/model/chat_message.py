from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, Integer
from sqlalchemy.orm import declarative_base
from util.datetime_util import now_beijing

Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = 'chat_message'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    qa_id = Column(String(64), nullable=False, unique=True)
    query = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    files = Column(JSON, nullable=True)
    response_time = Column(Integer, nullable=True)
    finish_time = Column(DateTime, nullable=True)
    series = Column(String(32), nullable=True)
    model_name = Column(String(64), nullable=True)
    model_type = Column(String(32), nullable=True)
    recall = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now_beijing)

    def __init__(
        self,
        session_id: str,
        qa_id: str,
        query: str = None,
        answer: str = None,
        files: list = None,
        response_time: int = None,
        finish_time: datetime = None,
        series: str = None,
        model_name: str = None,
        model_type: str = None,
        recall: str = None,
        reason: str = None
    ):
        self.session_id = session_id
        self.qa_id = qa_id
        self.query = query
        self.answer = answer
        self.files = files or []
        self.response_time = response_time
        self.finish_time = finish_time
        self.series = series
        self.model_name = model_name
        self.model_type = model_type
        self.recall = recall
        self.reason = reason
