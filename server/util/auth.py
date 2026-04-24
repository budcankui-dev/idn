import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from model.user import User
from crud.user_crud import UserCRUD
from util.db import get_db_singleton
from config.settings import get_settings

# 从配置加载认证相关配置
_settings = get_settings()
SECRET_KEY = _settings.auth.secret_key
ALGORITHM = _settings.auth.algorithm
ACCESS_TOKEN_EXPIRE_HOURS = _settings.auth.access_token_expire_hours

security = HTTPBearer()


def hash_password(password: str) -> str:
    """密码哈希"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def create_access_token(user_id: int, username: str, role: str) -> str:
    """创建JWT令牌"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的令牌")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """获取当前用户（依赖注入）"""
    token = credentials.credentials
    payload = decode_token(token)
    return {
        "user_id": int(payload.get("sub")),
        "username": payload.get("username"),
        "role": payload.get("role")
    }


def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前用户，要求是管理员"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


def get_db():
    """FastAPI 依赖：管理数据库会话生命周期"""
    db_session = get_db_singleton().get_session()
    try:
        yield db_session
    finally:
        db_session.close()
