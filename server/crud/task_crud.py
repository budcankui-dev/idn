from sqlalchemy.orm import Session
from model.task import Task
from typing import List, Optional


class TaskCRUD:

    @staticmethod
    def create(db: Session, task_obj: Task) -> Task:
        db.add(task_obj)
        db.commit()
        db.refresh(task_obj)
        return task_obj

    @staticmethod
    def get_by_id(db: Session, task_id: int) -> Optional[Task]:
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_by_session_id(db: Session, session_id: str) -> Optional[Task]:
        return db.query(Task).filter(Task.session_id == session_id).first()

    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(Task)\
            .filter(Task.user_id == user_id)\
            .order_by(Task.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(Task)\
            .order_by(Task.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def get_count(db: Session, user_id: int = None) -> int:
        query = db.query(Task)
        if user_id:
            query = query.filter(Task.user_id == user_id)
        return query.count()

    @staticmethod
    def update(db: Session, task_obj: Task, **kwargs) -> Task:
        for key, value in kwargs.items():
            if hasattr(task_obj, key):
                setattr(task_obj, key, value)
        db.commit()
        db.refresh(task_obj)
        return task_obj

    @staticmethod
    def delete(db: Session, task_obj: Task) -> None:
        db.delete(task_obj)
        db.commit()
