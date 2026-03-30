#!/usr/bin/env python
import os
from typing import List, Optional
from langchain.pydantic_v1 import Field
from fastapi import FastAPI
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage,SystemMessage
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langserve import add_routes, CustomUserType
from langchain.globals import set_debug
from system_messages import GenPrompt

set_debug(True)

os.environ["DASHSCOPE_API_KEY"] = "sk-6230e8709fac4500bb03733ebbb2ebee"

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

# model = ChatTongyi(model="qwen-turbo", streaming=True)
model = ChatTongyi(model="qwen-plus-2025-07-14", streaming=True)


class ChatTurn(CustomUserType):
    user: str
    assistant: Optional[str] = None


class ChatHistory(CustomUserType):
    prompt: str
    history: List[ChatTurn] = Field(default_factory=list)


def _format_to_messages(input: ChatHistory) -> List[BaseMessage]:
    """Format the input to a list of messages."""
    history = input.history
    user_input = input.prompt

    messages = []
    # 测试 选择第三种提示词策略（知识库+特定的思维链）
    # messages.append(SystemMessage(content="你是一个只会回答烹饪问题的助手，其他问题一律拒绝。")) 
    # messages.append(SystemMessage(content="注意回复的时候使用markdown的json格式输出"+GenPrompt(2)))
    messages.append(SystemMessage(content=GenPrompt(0)))
    for turn in history:
        messages.append(HumanMessage(content=turn.user))
        messages.append(AIMessage(content=turn.assistant))
    messages.append(HumanMessage(content=user_input))
    return messages


model = RunnableParallel({"data": (RunnableLambda(_format_to_messages) | model)})

add_routes(
    app,
    model.with_types(input_type=ChatHistory),
    path="/chat",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=5000)
