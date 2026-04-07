from sqlalchemy.orm import Session
from model.chat_session import ChatSession

class ChatSessionCRUD:

    @staticmethod
    def create(db: Session, session_obj: ChatSession):
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)
        return session_obj

    @staticmethod
    def get_by_session_id(db: Session, session_id: str):
        return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    @staticmethod
    def update(db: Session, session_obj: ChatSession, **kwargs):
        for key, value in kwargs.items():
            if hasattr(session_obj, key):
                setattr(session_obj, key, value)
        db.commit()
        db.refresh(session_obj)
        return session_obj

    @staticmethod
    def delete(db: Session, session_obj: ChatSession):
        db.delete(session_obj)
        db.commit()