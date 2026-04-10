from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from model.user import User
from crud.user_crud import UserCRUD
from util.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_db
)

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


class UserInfo(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db_session: Session = Depends(get_db)):
    """用户登录"""
    user = UserCRUD.get_by_username(db_session, data.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="账号已被禁用")

    access_token = create_access_token(user.id, user.username, user.role)
    return LoginResponse(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@router.get("/me", response_model=UserInfo)
def get_me(current_user: dict = Depends(get_current_user), db_session: Session = Depends(get_db)):
    """获取当前用户信息"""
    user = UserCRUD.get_by_id(db_session, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """用户登出（前端删除token即可）"""
    return {"message": "登出成功"}


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


@router.post("/register")
def register(data: RegisterRequest, db_session: Session = Depends(get_db)):
    """用户注册"""
    if UserCRUD.exists(db_session, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        email=data.email,
        role="normal",
        is_active=True
    )
    user = UserCRUD.create(db_session, user)
    return {"id": user.id, "username": user.username}
