from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from crud.task_crud import TaskCRUD
from crud.user_crud import UserCRUD
from util.auth import get_current_admin, get_db

router = APIRouter(prefix="/admin/tasks", tags=["管理员-任务"])


class AdminTaskResponse(BaseModel):
    id: int
    session_id: str
    user_id: int
    username: str
    business: str
    params: dict
    state: dict
    dag: dict
    created_at: datetime
    updated_at: datetime


class AdminTaskListResponse(BaseModel):
    tasks: List[AdminTaskResponse]
    total: int


# ============ Admin Task Endpoints ============

@router.get("", response_model=AdminTaskListResponse)
def admin_get_all_tasks(
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    current_user: dict = Depends(get_current_admin),
    db_session: Session = Depends(get_db)
):
    """管理员获取所有任务（支持真实分页，按用户筛选）"""
    if user_id:
        tasks = TaskCRUD.get_by_user(db_session, user_id, skip, limit)
        total = TaskCRUD.get_count(db_session, user_id)
    else:
        tasks = TaskCRUD.get_all(db_session, skip, limit)
        total = TaskCRUD.get_count(db_session)

    result = []
    for t in tasks:
        # 获取用户名
        user = UserCRUD.get_by_id(db_session, t.user_id)
        username = user.username if user else "未知"
        result.append(AdminTaskResponse(
            id=t.id,
            session_id=t.session_id,
            user_id=t.user_id,
            username=username,
            business=t.business,
            params=t.params,
            state=t.state,
            dag=t.dag,
            created_at=t.created_at,
            updated_at=t.updated_at
        ))

    return AdminTaskListResponse(tasks=result, total=total)


@router.delete("/{task_id}")
def admin_delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_admin),
    db_session: Session = Depends(get_db)
):
    """管理员删除任意任务"""
    task = TaskCRUD.get_by_id(db_session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    TaskCRUD.delete(db_session, task)
    return {"message": "任务已删除"}
