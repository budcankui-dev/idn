# main_db_api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pydantic import BaseModel
from typing import Optional, List, Dict

from crud.chat_session_crud import ChatSessionCRUD


from model.chat_session import ChatSession
from util.db import get_db_singleton


router = APIRouter(prefix="/session", tags=["ChatSession"])

# 请求体
class SubmitSession(BaseModel):
    session_id: str
    business: str
    prompt: Optional[str] = None
    history: Optional[List[Dict]] = None
    state: Dict
    params: Dict
    dag: Dict

class UpdateSession(BaseModel):
    prompt: Optional[str] = None
    history: Optional[List[Dict]] = None
    state: Optional[Dict] = None
    params: Optional[Dict] = None
    dag: Optional[Dict] = None

# 依赖
def get_db():
    """FastAPI 依赖：管理数据库会话生命周期"""
    db_session = get_db_singleton().get_session()
    try:
        yield db_session
    finally:
        db_session.close()

@router.post("/submit")
def submit_session(data: SubmitSession, db_session: Session = Depends(get_db)):
    
    existing = ChatSessionCRUD.get_by_session_id(db_session, data.session_id)
    if existing:
        raise HTTPException(status_code=400, detail="Session already exists")
    session_obj = ChatSession(
        session_id=data.session_id,
        business=data.business,
        prompt=data.prompt,
        history=data.history,
        state=data.state,
        params=data.params,
        dag=data.dag
    )
    session = ChatSessionCRUD.create(db_session, session_obj)
    return {"id": session.id, "session_id": session.session_id}

@router.get("/{session_id}")
def get_session(session_id: str, db_session: Session = Depends(get_db)):
    session = ChatSessionCRUD.get_by_session_id(db_session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": session.id,
        "session_id": session.session_id,
        "business": session.business,
        "prompt": session.prompt,
        "history": session.history,
        "state": session.state,
        "params": session.params,
        "dag": session.dag,
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }

@router.put("/{session_id}")
def update_session(session_id: str, data: UpdateSession, db_session: Session = Depends(get_db)):
    session = ChatSessionCRUD.get_by_session_id(db_session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    update_data = data.dict(exclude_unset=True)
    updated_session = ChatSessionCRUD.update(db_session, session, **update_data)
    return {
        "id": updated_session.id,
        "session_id": updated_session.session_id,
        "business": updated_session.business,
        "prompt": updated_session.prompt,
        "history": updated_session.history,
        "state": updated_session.state,
        "params": updated_session.params,
        "dag": updated_session.dag,
        "created_at": updated_session.created_at,
        "updated_at": updated_session.updated_at
    }

@router.delete("/{session_id}")
def delete_session(session_id: str, db_session: Session = Depends(get_db)):
    session = ChatSessionCRUD.get_by_session_id(db_session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    ChatSessionCRUD.delete(db_session, session)
    return {"message": "Session deleted successfully"}