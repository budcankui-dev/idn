#!/usr/bin/env python3
# test_dataset/one_case.py
"""
生成单条测试用例（用于前端调试）
直接调用 LLM，不走 HTTP 接口
"""

import os
import random
import re
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from templates import (
    VIDEO_INFERENCE_TEMPLATES,
    MODEL_TRAINING_TEMPLATES,
    SLOT_VALUES,
    replace_slots,
)

# ============ 直接复用 server 的 LLM 和解析逻辑 ============
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage
from parser.state import State
from parser.state_parser import parse_intent_output
from prompt.workflow_parse_intent import get_slot_parse_prompt

os.environ["DASHSCOPE_API_KEY"] = "sk-6230e8709fac4500bb03733ebbb2ebee"

llm = ChatTongyi(model="qwen-plus-2025-07-14", streaming=False)


def generate_one(business_type: str = None) -> dict:
    """生成一条测试用例"""
    if business_type is None:
        business_type = random.choice(["视频AI推理", "模型训练"])

    if business_type == "视频AI推理":
        templates = VIDEO_INFERENCE_TEMPLATES
    else:
        templates = MODEL_TRAINING_TEMPLATES

    template = random.choice(templates)
    slots_in_template = re.findall(r"\{(\w+)\}", template)

    slot_dict = {}
    for slot in slots_in_template:
        values = SLOT_VALUES.get(slot, [slot])
        slot_dict[slot] = random.choice(values)

    text = replace_slots(template, slot_dict)

    return {
        "text": text,
        "business_type": business_type,
        "slots": slot_dict,
    }


def call_llm(text: str, business_type: str = None, validate: bool = False) -> dict:
    """直接调用 LLM 进行意图解析"""
    state = State(session_id="test", workflow="intent_parsing")
    if business_type:
        state.intent_result = {"任务名称": business_type, "参数": {}}

    prompt = get_slot_parse_prompt(state)
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=text)
    ]

    try:
        result = llm.invoke(messages)
        full_text = result.content

        if not validate:
            state.intent_result = {}
            final_state = parse_intent_output(full_text, state, validate_values=False)
        else:
            final_state = parse_intent_output(full_text, state)

        return {
            "input": text,
            "business_type_hint": business_type,
            "validate": validate,
            "llm_output": full_text,
            "parsed_result": final_state.model_dump()
        }
    except Exception as e:
        return {"error": str(e), "text": text, "business_type": business_type}


def print_case(case: dict, idx: int = 1):
    """格式化打印一条 case"""
    print("=" * 60)
    print(f"[{idx}] 业务类型: {case['business_type']}")
    print(f"[{idx}] 用户输入: {case['text']}")
    print(f"[{idx}] 槽位值:   {case['slots']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="生成单条测试用例（前端调试用）")
    parser.add_argument(
        "--type", "-t",
        choices=["视频AI推理", "模型训练"],
        default=None,
        help="指定业务类型，不指定则随机",
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="生成几条（默认1条）",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="同时调用 LLM 解析（validate=False）",
    )
    args = parser.parse_args()

    for i in range(args.count):
        case = generate_one(args.type)
        print_case(case, i + 1)

        if args.api:
            print(f"[{i+1}] 调用 LLM...")
            result = call_llm(case["text"], case["business_type"], validate=False)
            print(f"[{i+1}] LLM 返回: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print()


if __name__ == "__main__":
    main()