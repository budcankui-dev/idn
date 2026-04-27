#!/usr/bin/env python
"""初始化数据库，创建管理员账号"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from util.db import get_db_singleton
from model.user import Base as UserBase, User
from model.chat_history import Base as ChatHistoryBase
from model.chat_message import Base as ChatMessageBase
from model.task import Base as TaskBase
from crud.user_crud import UserCRUD
from util.auth import hash_password


def init_database():
    """初始化数据库表"""
    db = get_db_singleton()

    # 创建所有表
    UserBase.metadata.create_all(bind=db.engine)
    ChatHistoryBase.metadata.create_all(bind=db.engine)
    ChatMessageBase.metadata.create_all(bind=db.engine)
    TaskBase.metadata.create_all(bind=db.engine)
    print("数据库表创建成功")


def create_admin_user(username: str = "admin", password: str = "admin123"):
    """创建管理员账号"""
    db = get_db_singleton()
    db_session = db.get_session()
    try:
        # 检查是否已存在
        existing = UserCRUD.get_by_username(db_session, username)
        if existing:
            print(f"用户 {username} 已存在，跳过创建")
            return

        # 创建管理员
        admin = User(
            username=username,
            password_hash=hash_password(password),
            email=None,
            role="admin",
            is_active=True
        )
        UserCRUD.create(db_session, admin)
        print(f"管理员账号创建成功: {username}/{password}")
    finally:
        db_session.close()


if __name__ == "__main__":
    print("开始初始化数据库...")
    init_database()
    create_admin_user()
    print("初始化完成")
