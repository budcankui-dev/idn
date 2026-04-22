from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from model.task import Task
from model.user import User
from crud.task_crud import TaskCRUD
from util.auth import get_current_user, get_db

router = APIRouter(prefix="/tasks", tags=["任务"])


# ============ Request/Response Models ============

class CreateTaskRequest(BaseModel):
    session_id: str
    business: str
    state: dict
    params: dict
    dag: dict


class UpdateTaskRequest(BaseModel):
    state: Optional[dict] = None
    params: Optional[dict] = None
    dag: Optional[dict] = None


class TaskResponse(BaseModel):
    id: int
    session_id: str
    user_id: int
    username: Optional[str] = None
    business: str
    state: dict
    params: dict
    dag: dict
    created_at: datetime
    updated_at: datetime


# ============ Task Endpoints ============

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """获取任务列表（普通用户只能看自己的，管理员看所有）"""
    if current_user["role"] == "admin":
        tasks = TaskCRUD.get_all(db_session, skip, limit)
    else:
        tasks = TaskCRUD.get_by_user(db_session, current_user["user_id"], skip, limit)

    # 获取所有相关用户名
    user_ids = list(set(t.user_id for t in tasks))
    users = db_session.query(User).filter(User.id.in_(user_ids)).all()
    username_map = {u.id: u.username for u in users}

    return [
        TaskResponse(
            id=t.id,
            session_id=t.session_id,
            user_id=t.user_id,
            username=username_map.get(t.user_id),
            business=t.business,
            state=t.state,
            params=t.params,
            dag=t.dag,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in tasks
    ]


@router.post("", response_model=TaskResponse)
def create_task(
    data: CreateTaskRequest,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """提交新任务"""
    existing = TaskCRUD.get_by_session_id(db_session, data.session_id)
    if existing:
        raise HTTPException(status_code=400, detail="任务已存在")

    # 如果 dag 为空，从 params 填充
    dag = data.dag if data.dag and len(data.dag) > 0 else {}
    print(f"[DEBUG] create_task: data.dag={data.dag}, dag={dag}")
    if not dag:
        from parser.state_parser import parse_duration, parse_start_time
        from parser.dag_template import VideoInferenceDAG, ModelTrainingDAG

        params = data.params.get("参数", {}) if isinstance(data.params, dict) else {}
        # 兼容"任务名称"和"业务类型"字段
        business_type = data.params.get("任务名称", "") if isinstance(data.params, dict) else ""
        if not business_type:
            business_type = data.params.get("业务类型", "") if isinstance(data.params, dict) else ""
        print(f"[DEBUG] create_task: params={params}, business_type={business_type}")

        if business_type == "视频AI推理":
            dag_template = VideoInferenceDAG(session_id=data.session_id)
            start_time_str = params.get("开始时间")
            if start_time_str:
                try:
                    dag_template.set_submit_ts_ms(parse_start_time(start_time_str))
                except Exception as e:
                    print(f"解析开始时间失败: {e}")
            duration_str = params.get("期望运行时间")
            if duration_str:
                try:
                    runtime_ms = parse_duration(duration_str, business_type)
                    dag_template.set_runtime(runtime_ms)
                except Exception as e:
                    print(f"解析运行时长失败: {e}")
            dag = dag_template.to_dict()
        elif business_type == "模型训练":
            dag_template = ModelTrainingDAG(session_id=data.session_id)
            start_time_str = params.get("开始时间")
            if start_time_str:
                try:
                    dag_template.set_submit_ts_ms(parse_start_time(start_time_str))
                except Exception as e:
                    print(f"解析开始时间失败: {e}")
            duration_str = params.get("期望运行时间")
            if duration_str:
                try:
                    runtime_ms = parse_duration(duration_str, business_type)
                    dag_template.set_runtime(runtime_ms)
                except Exception as e:
                    print(f"解析运行时长失败: {e}")
            dag = dag_template.to_dict()

    print(f"[DEBUG] create_task: final dag={dag}")

    # 保留原始 state，不把 dag 存入 state（dag 只存 dag 字段）
    state = data.state.copy() if isinstance(data.state, dict) else {}

    task = Task(
        session_id=data.session_id,
        user_id=current_user["user_id"],
        business=data.business,
        state=state,
        params=data.params,
        dag=dag
    )
    task = TaskCRUD.create(db_session, task)
    return TaskResponse(
        id=task.id,
        session_id=task.session_id,
        user_id=task.user_id,
        business=task.business,
        state=task.state,
        params=task.params,
        dag=task.dag,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """获取任务详情"""
    task = TaskCRUD.get_by_id(db_session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此任务")

    return TaskResponse(
        id=task.id,
        session_id=task.session_id,
        user_id=task.user_id,
        business=task.business,
        state=task.state,
        params=task.params,
        dag=task.dag,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: UpdateTaskRequest,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """更新任务"""
    task = TaskCRUD.get_by_id(db_session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权修改此任务")

    update_data = data.dict(exclude_unset=True)
    task = TaskCRUD.update(db_session, task, **update_data)

    return TaskResponse(
        id=task.id,
        session_id=task.session_id,
        user_id=task.user_id,
        business=task.business,
        state=task.state,
        params=task.params,
        dag=task.dag,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """删除任务"""
    task = TaskCRUD.get_by_id(db_session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权删除此任务")

    TaskCRUD.delete(db_session, task)
    return {"message": "任务已删除"}
