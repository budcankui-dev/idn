from sqlalchemy.orm import Session
from model.chat_history import ChatHistory
from typing import List, Optional


class ChatHistoryCRUD:

    @staticmethod
    def create(db: Session, history_obj: ChatHistory) -> ChatHistory:
        db.add(history_obj)
        db.commit()
        db.refresh(history_obj)
        return history_obj

    @staticmethod
    def get_by_id(db: Session, history_id: int) -> Optional[ChatHistory]:
        return db.query(ChatHistory).filter(ChatHistory.id == history_id).first()

    @staticmethod
    def get_by_session_id(db: Session, session_id: str) -> Optional[ChatHistory]:
        return db.query(ChatHistory).filter(ChatHistory.session_id == session_id).first()

    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatHistory]:
        return db.query(ChatHistory)\
            .filter(ChatHistory.user_id == user_id)\
            .order_by(ChatHistory.updated_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def update(db: Session, history_obj: ChatHistory, **kwargs) -> ChatHistory:
        for key, value in kwargs.items():
            if hasattr(history_obj, key):
                setattr(history_obj, key, value)
        db.commit()
        db.refresh(history_obj)
        return history_obj

    @staticmethod
    def update_state(db: Session, session_id: str, state: dict) -> Optional[ChatHistory]:
        """更新会话状态"""
        history_obj = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).first()
        if history_obj:
            history_obj.state = state
            db.commit()
            db.refresh(history_obj)
        return history_obj

    @staticmethod
    def delete(db: Session, history_obj: ChatHistory) -> None:
        db.delete(history_obj)
        db.commit()
