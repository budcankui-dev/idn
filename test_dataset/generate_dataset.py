#!/usr/bin/env python3
# test_dataset/generate_dataset.py
"""
数据集生成脚本
直接调用 LLM，单线程 + retry，tqdm 进度显示，边生成边保存
"""

import os
import sys
import json
import random
import re
import itertools
import time
from typing import List, Dict, Tuple

from tqdm import tqdm

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from templates import (
    VIDEO_INFERENCE_TEMPLATES,
    MODEL_TRAINING_TEMPLATES,
    SLOT_VALUES,
    replace_slots,
)
from parser.state import State
from parser.state_parser import parse_intent_output
from prompt.workflow_parse_intent import get_slot_parse_prompt

os.environ["DASHSCOPE_API_KEY"] = "sk-6230e8709fac4500bb03733ebbb2ebee"

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatTongyi(model="qwen-plus-2025-07-14", streaming=False)

MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒


def call_llm_parse(text: str, business_type: str = None, validate: bool = False) -> Dict:
    """调用 LLM，单线程 + retry"""
    state = State(session_id="test", workflow="intent_parsing")
    if business_type:
        state.intent_result = {"任务名称": business_type, "参数": {}}

    prompt = get_slot_parse_prompt(state)
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=text)
    ]

    last_error = None
    for attempt in range(MAX_RETRIES):
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
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

    return {"error": last_error, "text": text, "business_type": business_type}


def load_templates() -> List[Dict]:
    return [
        {"type": "视频AI推理", "templates": VIDEO_INFERENCE_TEMPLATES},
        {"type": "模型训练", "templates": MODEL_TRAINING_TEMPLATES},
    ]


def generate_one_case(template: str, business_type: str, slot_values: Dict) -> Dict:
    text = replace_slots(template, slot_values)
    return {"text": text, "business_type": business_type, "slots": slot_values}


def generate_dataset_texts(n_train: int, n_val: int) -> Tuple[List[Dict], List[Dict]]:
    all_cases = []
    for td in load_templates():
        business_type = td["type"]
        for template in td["templates"]:
            slots = re.findall(r"\{(\w+)\}", template)
            value_lists = [SLOT_VALUES.get(s, [s]) for s in slots]
            for combination in itertools.product(*value_lists):
                slot_dict = dict(zip(slots, combination))
                all_cases.append(generate_one_case(template, business_type, slot_dict))

    random.shuffle(all_cases)
    total = n_train + n_val
    if len(all_cases) >= total:
        sampled = random.sample(all_cases, total)
    else:
        sampled = []
        while len(sampled) < total:
            sampled.extend(random.sample(all_cases, min(len(all_cases), total - len(sampled))))

    return sampled[:n_train], sampled[n_train:n_train + n_val]


def generate_and_save(
    output_path: str,
    cases: List[Dict],
    validate: bool = False,
    desc: str = "生成",
):
    """单线程顺序调用 LLM，边生成边写入文件，tqdm 进度显示"""
    errors = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for case in tqdm(cases, desc=desc, unit="条"):
            result = call_llm_parse(case["text"], case["business_type"], validate=validate)
            case["api_result"] = result
            if "error" in result:
                errors += 1
            f.write(json.dumps(case, ensure_ascii=False) + "\n")
            f.flush()

    print(f"  {desc}: {len(cases)} 条, {errors} 个错误 -> {output_path}")


def generate_jsonl(
    train_output: str = "train.jsonl",
    val_output: str = "val.jsonl",
    n_train: int = 800,
    n_val: int = 200,
    validate: bool = False,
):
    print(f"正在生成 {n_train} 条训练数据 + {n_val} 条验证数据...")

    train_cases, val_cases = generate_dataset_texts(n_train, n_val)

    print("开始调用 LLM（单线程 + retry）...")

    # 先写训练集
    generate_and_save(train_output, train_cases, validate=validate, desc="训练集")
    # 再写验证集
    generate_and_save(val_output, val_cases, validate=validate, desc="验证集")

    print("数据集生成完成!")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="生成意图解析测试数据集")
    parser.add_argument("--train", type=int, default=800)
    parser.add_argument("--val", type=int, default=200)
    parser.add_argument("--output-dir", type=str, default=".")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    train_path = os.path.join(args.output_dir, "train.jsonl")
    val_path = os.path.join(args.output_dir, "val.jsonl")

    generate_jsonl(train_path, val_path, args.train, args.val, args.validate)


if __name__ == "__main__":
    main()