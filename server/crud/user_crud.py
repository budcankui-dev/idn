from sqlalchemy.orm import Session
from model.user import User
from typing import Optional, List


class UserCRUD:

    @staticmethod
    def create(db: Session, user_obj: User) -> User:
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
        return user_obj

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def get_count(db: Session) -> int:
        return db.query(User).count()

    @staticmethod
    def update(db: Session, user_obj: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if hasattr(user_obj, key) and key != 'id':
                setattr(user_obj, key, value)
        db.commit()
        db.refresh(user_obj)
        return user_obj

    @staticmethod
    def delete(db: Session, user_obj: User) -> None:
        db.delete(user_obj)
        db.commit()

    @staticmethod
    def exists(db: Session, username: str) -> bool:
        return db.query(User).filter(User.username == username).first() is not None
