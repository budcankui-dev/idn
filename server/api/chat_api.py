from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from model.chat_history import ChatHistory
from model.chat_message import ChatMessage
from crud.chat_history_crud import ChatHistoryCRUD
from crud.chat_message_crud import ChatMessageCRUD
from util.auth import get_current_user, get_db

router = APIRouter(prefix="/chat", tags=["聊天"])


# ============ Request/Response Models ============

class CreateSessionRequest(BaseModel):
    session_id: str
    title: Optional[str] = ''


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None


class UpdateStateRequest(BaseModel):
    state: dict


class MessageRequest(BaseModel):
    qa_id: str
    query: Optional[str] = None
    answer: Optional[str] = None
    files: Optional[List[dict]] = None
    response_time: Optional[int] = None
    finish_time: Optional[datetime] = None
    series: Optional[str] = None
    model_name: Optional[str] = None
    model_type: Optional[str] = None
    recall: Optional[str] = None
    reason: Optional[str] = None


class UpdateMessageRequest(BaseModel):
    answer: Optional[str] = None
    files: Optional[List[dict]] = None
    response_time: Optional[int] = None
    finish_time: Optional[datetime] = None


class ChatHistoryResponse(BaseModel):
    session_id: str
    title: str
    state: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class SessionStateResponse(BaseModel):
    session_id: str
    state: dict


class ChatMessageResponse(BaseModel):
    qa_id: str
    query: Optional[str]
    answer: Optional[str]
    files: Optional[List[dict]]
    response_time: Optional[int]
    finish_time: Optional[datetime]
    series: Optional[str]
    model_name: Optional[str]
    model_type: Optional[str]
    recall: Optional[str]
    reason: Optional[str]
    created_at: datetime


# ============ Chat History Endpoints ============

@router.get("/history", response_model=List[ChatHistoryResponse])
def get_chat_histories(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """获取当前用户的聊天会话列表"""
    histories = ChatHistoryCRUD.get_by_user(db_session, current_user["user_id"], skip, limit)
    return [
        ChatHistoryResponse(
            session_id=h.session_id,
            title=h.title,
            state=h.state,
            created_at=h.created_at,
            updated_at=h.updated_at
        )
        for h in histories
    ]


@router.post("/history", response_model=ChatHistoryResponse)
def create_chat_history(
    data: CreateSessionRequest,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """创建新的聊天会话"""
    existing = ChatHistoryCRUD.get_by_session_id(db_session, data.session_id)
    if existing:
        raise HTTPException(status_code=400, detail="会话已存在")

    history = ChatHistory(
        session_id=data.session_id,
        user_id=current_user["user_id"],
        title=data.title or ''
    )
    history = ChatHistoryCRUD.create(db_session, history)
    return ChatHistoryResponse(
        session_id=history.session_id,
        title=history.title,
        created_at=history.created_at,
        updated_at=history.updated_at
    )


@router.delete("/history/{session_id}")
def delete_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """删除聊天会话及其所有消息"""
    history = ChatHistoryCRUD.get_by_session_id(db_session, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="会话不存在")

    if history.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权删除此会话")

    # 删除关联的消息
    ChatMessageCRUD.delete_by_session(db_session, session_id)
    # 删除会话
    ChatHistoryCRUD.delete(db_session, history)
    return {"message": "会话已删除"}


@router.put("/history/{session_id}", response_model=ChatHistoryResponse)
def update_chat_history(
    session_id: str,
    data: UpdateSessionRequest,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """更新聊天会话"""
    history = ChatHistoryCRUD.get_by_session_id(db_session, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="会话不存在")

    if history.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权更新此会话")

    if data.title is not None:
        history.title = data.title
    ChatHistoryCRUD.update(db_session, history)
    return ChatHistoryResponse(
        session_id=history.session_id,
        title=history.title,
        state=history.state,
        created_at=history.created_at,
        updated_at=history.updated_at
    )


# ============ Session State Endpoints ============

@router.get("/history/{session_id}/state", response_model=SessionStateResponse)
def get_session_state(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """获取会话状态（用于刷新后恢复）"""
    history = ChatHistoryCRUD.get_by_session_id(db_session, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="会话不存在")

    if history.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此会话")

    return SessionStateResponse(
        session_id=session_id,
        state=history.state or {}
    )


@router.put("/history/{session_id}/state", response_model=SessionStateResponse)
def update_session_state(
    session_id: str,
    data: UpdateStateRequest,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """更新会话状态（实时保存解析结果）"""
    history = ChatHistoryCRUD.get_by_session_id(db_session, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="会话不存在")

    if history.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权更新此会话")

    ChatHistoryCRUD.update_state(db_session, session_id, data.state)

    return SessionStateResponse(
        session_id=session_id,
        state=data.state
    )


# ============ Chat Message Endpoints ============

@router.get("/history/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """获取会话的所有消息"""
    history = ChatHistoryCRUD.get_by_session_id(db_session, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="会话不存在")

    if history.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此会话")

    messages = ChatMessageCRUD.get_by_session(db_session, session_id)
    return [
        ChatMessageResponse(
            qa_id=m.qa_id,
            query=m.query,
            answer=m.answer,
            files=m.files,
            response_time=m.response_time,
            finish_time=m.finish_time,
            series=m.series,
            model_name=m.model_name,
            model_type=m.model_type,
            recall=m.recall,
            reason=m.reason,
            created_at=m.created_at
        )
        for m in messages
    ]


@router.post("/history/{session_id}/messages", response_model=ChatMessageResponse)
def create_chat_message(
    session_id: str,
    data: MessageRequest,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """添加新消息到会话"""
    history = ChatHistoryCRUD.get_by_session_id(db_session, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="会话不存在")

    if history.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此会话")

    existing = ChatMessageCRUD.get_by_qa_id(db_session, data.qa_id)
    if existing:
        raise HTTPException(status_code=400, detail="消息已存在")

    message = ChatMessage(
        session_id=session_id,
        qa_id=data.qa_id,
        query=data.query,
        answer=data.answer,
        files=data.files,
        response_time=data.response_time,
        finish_time=data.finish_time,
        series=data.series,
        model_name=data.model_name,
        model_type=data.model_type,
        recall=data.recall,
        reason=data.reason
    )
    message = ChatMessageCRUD.create(db_session, message)

    # 更新会话的 updated_at
    ChatHistoryCRUD.update(db_session, history)

    return ChatMessageResponse(
        qa_id=message.qa_id,
        query=message.query,
        answer=message.answer,
        files=message.files,
        response_time=message.response_time,
        finish_time=message.finish_time,
        series=message.series,
        model_name=message.model_name,
        model_type=message.model_type,
        recall=message.recall,
        reason=message.reason,
        created_at=message.created_at
    )


@router.put("/message/{qa_id}", response_model=ChatMessageResponse)
def update_chat_message(
    qa_id: str,
    data: UpdateMessageRequest,
    current_user: dict = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    """更新消息（如设置答案）"""
    message = ChatMessageCRUD.get_by_qa_id(db_session, qa_id)
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    # 检查用户权限
    history = ChatHistoryCRUD.get_by_session_id(db_session, message.session_id)
    if history.user_id != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权修改此消息")

    update_data = data.dict(exclude_unset=True)
    message = ChatMessageCRUD.update(db_session, message, **update_data)

    return ChatMessageResponse(
        qa_id=message.qa_id,
        query=message.query,
        answer=message.answer,
        files=message.files,
        response_time=message.response_time,
        finish_time=message.finish_time,
        series=message.series,
        model_name=message.model_name,
        model_type=message.model_type,
        recall=message.recall,
        reason=message.reason,
        created_at=message.created_at
    )
