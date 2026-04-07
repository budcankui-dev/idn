

import json
import re
from typing import Optional
from datetime import datetime
import dateparser
from parser.state import State

# 最低运行时长阈值：单位毫秒
MIN_RUNTIME_MS = 5 * 60 * 1000  # 5分钟

VIDEO_KEY_PARAMS = ["模型名称", "延迟", "视频帧率", "分辨率","模态","开始时间","期望运行时间"]
TRAIN_KEY_PARAMS = ["模型名称", "数据集", "训练轮次","模态","开始时间","期望运行时间"]

from parser.dag_template import VIDEO_DAG_TEMPLATE, TRAIN_DAG_TEMPLATE

# ---------------------- 时间解析 ----------------------
from datetime import datetime
import dateparser

def parse_start_time(user_input: str) -> int:
    dt = dateparser.parse(
        user_input,
        languages=['zh'],
        settings={'TIMEZONE': 'Asia/Shanghai', 'RETURN_AS_TIMEZONE_AWARE': False}
    )
    if not dt:
        raise ValueError("无法解析开始时间，请使用 'YYYY-MM-DD HH:MM'格式")
    if dt < datetime.now():
        raise ValueError("开始时间不能早于当前时间")
    return int(dt.timestamp() * 1000)

def parse_duration(user_input: str) -> int:
    pattern = r'(?:(\d+)\s*小时)?\s*(?:(\d+)\s*分钟)?\s*(?:(\d+)\s*秒)?'
    match = re.search(pattern, user_input)
    if not match:
        raise ValueError("无法解析运行时长")
    hours, minutes, seconds = match.groups(default="0")
    total_ms = int(hours) * 3600 * 1000 + int(minutes) * 60 * 1000 + int(seconds) * 1000
    if total_ms < MIN_RUNTIME_MS:
        raise ValueError(f"运行时长必须大于等于 {MIN_RUNTIME_MS//1000//60} 分钟")
    return total_ms

# ---------------------- 意图解析 ----------------------
def parse_intent_output(llm_text: str, state: Optional[State] = None) -> State:
    if state is None:
        state = State()

    if state.workflow == "dag":
            state.workflow = "dag"
            return state
    if state.workflow != "intent_parsing":
        state.code = -1
        state.msg = "未知的工作流"
        return state
  

    # 1. 提取 JSON
    json_str = ""
    match = re.search(r"```json(.*?)```", llm_text, re.DOTALL | re.IGNORECASE)
    if match:
        json_str = match.group(1).strip()
    else:
        first_brace = llm_text.find("{")
        last_brace = llm_text.rfind("}")
        if first_brace != -1 and last_brace != -1:
            json_str = llm_text[first_brace:last_brace+1]

    # 2. 解析 JSON
    try:
        json_res = json.loads(json_str)
    except Exception as e:
        state.code = -1
        state.msg = f"JSON解析失败: {e}"
        return state

    state.intent_result = json_res
    business_type = json_res.get("业务类型")
    params = json_res.get("参数", {})

    # ---------------------- 参数校验 ----------------------
    missing_params = []
    reason_params = []

    if business_type == "视频AI推理":
        key_params = VIDEO_KEY_PARAMS
    elif business_type == "AI模型训练":
        key_params = TRAIN_KEY_PARAMS
    else:
        key_params = VIDEO_KEY_PARAMS  # 保证字段校验
        reason_params.append({"param": "业务类型", "reason": f"未知业务类型: {business_type}"})
        if not business_type:
            missing_params.append("业务类型")

    for k in key_params:
        v = params.get(k)
        if v is None or v == "":
            missing_params.append(k)
        else:
            if k in ["延迟", "视频帧率"]:
                try:
                    if float(v) <= 0:
                        reason_params.append({"param": k, "reason": "必须大于0"})
                except:
                    reason_params.append({"param": k, "reason": "必须为数字"})
            elif k == "训练轮次":
                try:
                    if int(v) <= 0:
                        reason_params.append({"param": k, "reason": "必须大于0"})
                except:
                    reason_params.append({"param": k, "reason": "必须为整数"})
            elif k == "分辨率":
                if not re.match(r"^\d+x\d+$", str(v)):
                    reason_params.append({"param": k, "reason": "格式应为 WxH，如 1920x1080"})
            elif k == "开始时间":
                try:
                    parse_start_time(v)
                except Exception as e:
                    reason_params.append({"param": k, "reason": str(e)})
            elif k == "期望运行时间":
                try:
                    parse_duration(v)
                except Exception as e:
                    reason_params.append({"param": k, "reason": str(e)})

    state.missing_params = missing_params
    state.reason_params = reason_params
    state.stage = "ask_missing" if missing_params or reason_params else "complete"
    state.parse_success = (
    business_type in ["视频AI推理", "AI模型训练"] and
    len(missing_params) == 0 and
    len(reason_params) == 0)

    # ---------------------- DAG 填充 ----------------------
    if state.parse_success and state.stage == "complete":
        if business_type == "视频AI推理":
            dag = json.loads(json.dumps(VIDEO_DAG_TEMPLATE))  # 深拷贝
        else:
            dag = json.loads(json.dumps(TRAIN_DAG_TEMPLATE))

        # 填充 submit_ts_ms
        start_time_str = params.get("开始时间")
        if start_time_str:
            dag["submit_ts_ms"] = parse_start_time(start_time_str)

        # 填充每个节点 est_runtime_ms
        duration_str = params.get("期望运行时间")
        if duration_str:
            runtime_ms = parse_duration(duration_str)
            for node in dag.get("nodes", []):
                node["exec"]["est_runtime_ms"] = runtime_ms

        state.dag = dag

    return state