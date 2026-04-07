#!/usr/bin/env python
import os
import sys
import json
from typing import List, Optional

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from prompt.workflow_dag import get_dag_prompt
from prompt.workflow_parse_intent import get_intent_parse_prompt,get_slot_parse_prompt,get_followup_parse_prompt

from parser.state import State
from parser.state_parser import parse_intent_output

os.environ["DASHSCOPE_API_KEY"] = "sk-6230e8709fac4500bb03733ebbb2ebee"



app = FastAPI(title="智算业务助手", version="1.0")

# 数据库api
from api.db_api import router as db_router
app.include_router(db_router)

# ===== 数据结构 =====
class ChatTurn(BaseModel):
    user: str
    assistant: Optional[str] = None


class ChatData(BaseModel):
    prompt: str
    history: List[ChatTurn] = Field(default_factory=list)
    files: Optional[List[dict]] = Field(default_factory=list)
    # state: Optional[dict] = Field(default_factory=dict)  # stage等信息
    state: State = Field(default_factory=State)


# ===== 模型 =====
llm = ChatTongyi(model="qwen-plus-2025-07-14", streaming=True)

# ===== 消息转换 =====
def format_to_messages(data: ChatData,sys_prompt) -> List[BaseMessage]:
    messages: List[BaseMessage] = []
    if sys_prompt:
        messages.append(SystemMessage(content=sys_prompt))
    # 历史消息
    for turn in data.history:
        messages.append(HumanMessage(content=turn.user))
        if turn.assistant:
            messages.append(AIMessage(content=turn.assistant))
    # 最新用户输入
    messages.append(HumanMessage(content=data.prompt))
    return messages

def update_system_message(messages: List[BaseMessage], new_content: str):
    """
    更新 messages 中的 system 消息，如果没有就添加一个。
    messages: List[Dict], 每个 dict 至少包含 role 和 content
    new_content: str, 新的 system 消息内容
    """
    system_updated = False
    for msg in messages:
        if msg.type == "system":
            msg.content = new_content
            system_updated = True
            break
    if not system_updated:
        # 没有 system 消息，添加一个
        messages.insert(0, SystemMessage(content=new_content))
    return messages

async def parse_intent_workflow(llm, messages: List[BaseMessage], state: State):
    """
    流式调用 LLM 进行意图解析。
    - 解析调用两次 LLM：一次槽位抽取，一次补全
    """
   
    slot_prompt = get_slot_parse_prompt()
    update_system_message(messages, slot_prompt)
    slot_full_text = ""
    async for chunk in llm.astream(messages):
        if chunk.content:
            slot_full_text += chunk.content
            # yield f"data: {json.dumps({'content': chunk.content})}\n\n"

    # 解析状态
    slot_state = parse_intent_output(slot_full_text, state)
    print("**slot_state:**" * 20)
    print("slot_state:", slot_state)
    print("**slot_state:**" * 20)

    yield f"data: {json.dumps(slot_state.model_dump())}\n\n"

    # 为补全/追问准备 messages，上下文保留
    messages.append(AIMessage(content=slot_full_text))


    # ==== 补全/追问逻辑 ====
    followup_prompt = get_followup_parse_prompt(slot_state)
    update_system_message(messages, followup_prompt)
    full_text = ""
    async for chunk in llm.astream(messages):
        if chunk.content:
            full_text += chunk.content
            yield f"data: {json.dumps({'content': chunk.content})}\n\n"

    # 解析最终状态
    final_state = parse_intent_output(full_text, slot_state)
    print("**final_state:**"*20)
    print("final_state:", final_state)
    print("**final_state:**"*20)
    yield f"data: {json.dumps(final_state.model_dump())}\n\n"

    yield "data: [DONE]\n\n"

async def parse_dag_workflow(llm, messages: List[BaseMessage], state: State):
    """
    流式调用 LLM 执行 DAG 工作流。
    - 支持状态追踪
    - 与 parse_intent_workflow 风格一致
    """
    # 使用 DAG 提示词
    sys_prompt = get_dag_prompt(state)
    update_system_message(messages, sys_prompt)

    full_text = ""
    async for chunk in llm.astream(messages):
        if chunk.content:
            full_text += chunk.content
            yield f"data: {json.dumps({'content': chunk.content})}\n\n"

    # 解析最终状态
    final_state = parse_intent_output(full_text, state)
    yield f"data: {json.dumps(final_state.model_dump())}\n\n"
    yield "data: [DONE]\n\n"


# ===== 单接口流式返回 =====
@app.post("/chat/stream")
async def chat_api(data: ChatData):
    # print(data)
    workflow=data.state.workflow
    messages = format_to_messages(data, sys_prompt=None)  # 初始 messages，不加 system prompt
    if workflow=="intent_parsing":
        messages=format_to_messages(data,sys_prompt=None)
        return StreamingResponse(parse_intent_workflow(llm, messages, data.state), media_type="text/event-stream")
    elif workflow=="dag":
        return StreamingResponse(parse_dag_workflow(llm, messages, data.state),
                                 media_type="text/event-stream")
    else:
        return JSONResponse(content={"error": "Unknown workflow"})
   

@app.post("/chat/slot_extract")
async def chat_slot_extract(data: ChatData):
    """
    仅测试第一次解析时槽位抽取能力
    """
    # 构建消息
    messages = format_to_messages(data, sys_prompt=get_slot_parse_prompt())
    # 异步调用模型
    result = await llm.ainvoke(messages)
    full_text = result.content

    # 解析槽位状态
    final_state = parse_intent_output(full_text, data.state)
    return JSONResponse(content=jsonable_encoder({
        "content": full_text,
        "slot_state": final_state.model_dump()
    }))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6000)