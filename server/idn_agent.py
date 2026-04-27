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
from api.auth_api import router as auth_router
from api.user_api import router as user_router
from api.chat_api import router as chat_router
from api.task_api import router as task_router
from api.admin_task_api import router as admin_task_router
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(task_router)
app.include_router(admin_task_router)

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

def get_last_user_input(messages: List[BaseMessage]) -> str:
    """从消息历史中提取最后一个用户输入"""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


async def parse_intent_workflow(llm, messages: List[BaseMessage], state: State):
    """
    流式调用 LLM 进行意图解析。
    - 解析调用两次 LLM：一次槽位抽取，一次补全
    """
    # 提取用户原始输入（用于策略检测）
    user_input = get_last_user_input(messages)

    slot_prompt = get_slot_parse_prompt()
    update_system_message(messages, slot_prompt)
    slot_full_text = ""
    async for chunk in llm.astream(messages):
        if chunk.content:
            slot_full_text += chunk.content

    # 解析状态（不填充 DAG，DAG 在提交时才填充）
    slot_state = parse_intent_output(slot_full_text, state, fill_dag=False, user_input=user_input)
    print("slot_state"+"*" * 20)
    print("slot_state:", slot_state)

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

    # 解析最终状态（填充 DAG），传入 user_input 用于策略检测
    final_state = parse_intent_output(full_text, slot_state, fill_dag=True, user_input=user_input)

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
    print("Received data:"+"*" * 20)
    print(data)
    print(data.state)
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
    messages = format_to_messages(data, sys_prompt=get_slot_parse_prompt(data.state))
    # 异步调用模型
    result = await llm.ainvoke(messages)
    full_text = result.content

    # 解析槽位状态
    final_state = parse_intent_output(full_text, data.state, user_input=data.prompt)
    return JSONResponse(content=jsonable_encoder({
        "content": full_text,
        "state": final_state.model_dump()
    }))


class ParseTestRequest(BaseModel):
    """测试意图解析的简化请求"""
    text: str  # 用户输入文本
    business_type: Optional[str] = None  # 可选的业务类型 hint，如"视频AI推理"
    validate: bool = False  # 是否校验参数值合法性，默认False只做槽位抽取


@app.post("/parse/test")
async def parse_test(data: ParseTestRequest):
    """
    测试意图解析的简化接口，用于构造数据集。
    - 只做槽位抽取，判断参数是否存在
    - 不校验参数值是否合法（如延迟必须>0）
    - 提供 validate 参数控制是否校验，默认关闭
    """
    from langchain_core.messages import HumanMessage, SystemMessage

    # 构建提示词
    state = State(session_id="test", workflow="intent_parsing")
    if data.business_type:
        state.intent_result = {"任务名称": data.business_type, "参数": {}}

    prompt = get_slot_parse_prompt(state)

    # 构造消息
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=data.text)
    ]

    # 调用模型
    result = await llm.ainvoke(messages)
    full_text = result.content

    # 解析状态（不做参数值校验，只检查参数是否存在）
    if not data.validate:
        # 只做槽位抽取，设置一个标志跳过参数值校验
        state.intent_result = {}
        final_state = parse_intent_output(full_text, state, validate_values=False, user_input=data.text)
    else:
        final_state = parse_intent_output(full_text, state, user_input=data.text)

    return JSONResponse(content=jsonable_encoder({
        "input": data.text,
        "business_type_hint": data.business_type,
        "validate": data.validate,
        "llm_output": full_text,
        "parsed_result": final_state.model_dump()
    }))


@app.get("/parse/test")
async def parse_test_get():
    """GET 方法返回接口说明"""
    return {
        "method": "POST",
        "path": "/parse/test",
        "description": "测试意图解析的简化接口，用于构造数据集",
        "request_body": {
            "text": "用户输入文本，如：我想部署视频AI推理业务，用yolov8模型，延迟2秒，源终端h1，目的终端h2",
            "business_type": "可选的业务类型hint，如：视频AI推理"
        },
        "response": {
            "input": "原始输入",
            "business_type_hint": "业务类型hint",
            "llm_output": "LLM原始输出",
            "parsed_result": "解析后的状态对象，包含 intent_result、parse_success 等"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6000)