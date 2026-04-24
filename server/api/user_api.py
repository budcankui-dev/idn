from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from model.user import User
from crud.user_crud import UserCRUD
from util.auth import hash_password, get_current_admin, get_db

router = APIRouter(prefix="/users", tags=["用户管理"])


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: str = "normal"
    is_active: bool = True


class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    is_active: bool


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int


@router.get("", response_model=UserListResponse)
def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_admin),
    db_session: Session = Depends(get_db)
):
    """获取用户列表（仅管理员）- 支持真实分页"""
    users = UserCRUD.get_all(db_session, skip=skip, limit=limit)
    total = UserCRUD.get_count(db_session)
    return UserListResponse(
        users=[
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                is_active=u.is_active
            )
            for u in users
        ],
        total=total
    )


@router.post("", response_model=UserResponse)
def create_user(
    data: CreateUserRequest,
    current_user: dict = Depends(get_current_admin),
    db_session: Session = Depends(get_db)
):
    """创建用户（仅管理员）"""
    if UserCRUD.exists(db_session, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        email=data.email,
        role=data.role,
        is_active=data.is_active
    )
    user = UserCRUD.create(db_session, user)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UpdateUserRequest,
    current_user: dict = Depends(get_current_admin),
    db_session: Session = Depends(get_db)
):
    """更新用户（仅管理员）"""
    user = UserCRUD.get_by_id(db_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = data.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    user = UserCRUD.update(db_session, user, **update_data)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_admin),
    db_session: Session = Depends(get_db)
):
    """删除用户（仅管理员）"""
    user = UserCRUD.get_by_id(db_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="不能删除自己")

    UserCRUD.delete(db_session, user)
    return {"message": "用户已删除"}
