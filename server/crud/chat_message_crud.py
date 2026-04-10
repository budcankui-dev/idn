from sqlalchemy.orm import Session
from model.chat_message import ChatMessage
from typing import List, Optional


class ChatMessageCRUD:

    @staticmethod
    def create(db: Session, message_obj: ChatMessage) -> ChatMessage:
        db.add(message_obj)
        db.commit()
        db.refresh(message_obj)
        return message_obj

    @staticmethod
    def get_by_id(db: Session, message_id: int) -> Optional[ChatMessage]:
        return db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    @staticmethod
    def get_by_qa_id(db: Session, qa_id: str) -> Optional[ChatMessage]:
        return db.query(ChatMessage).filter(ChatMessage.qa_id == qa_id).first()

    @staticmethod
    def get_by_session(db: Session, session_id: str) -> List[ChatMessage]:
        return db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .all()

    @staticmethod
    def update(db: Session, message_obj: ChatMessage, **kwargs) -> ChatMessage:
        for key, value in kwargs.items():
            if hasattr(message_obj, key):
                setattr(message_obj, key, value)
        db.commit()
        db.refresh(message_obj)
        return message_obj

    @staticmethod
    def delete(db: Session, message_obj: ChatMessage) -> None:
        db.delete(message_obj)
        db.commit()

    @staticmethod
    def delete_by_session(db: Session, session_id: str) -> None:
        db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        db.commit()
