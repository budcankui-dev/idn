# server/parser/state_parser.py
"""
意图解析器 - 使用 BusinessConfig 统一管理业务配置
"""

import json
import re
from typing import Optional
from datetime import datetime
import dateparser
from parser.state import State
from parser.dag_template import VideoInferenceDAG, ModelTrainingDAG
from config.business_config import (
    get_business_config,
    BusinessType,
    VideoInferenceConfig,
    BUSINESS_CONFIG_REGISTRY,
)
from util.terminal_map import enrich_terminal_params


# ---------------------- 策略检测函数 ----------------------

DEFAULT_STRATEGY = "RESOURCE_GUARANTEE"

STRATEGY_KEYWORDS = {
    "TIME_CONSTRAINED": [
        # 明确表达时间优先策略的词组
       "更快", "尽快", "最快", "优先时间", "尽快完成", "最短时间", "优先保证时间",
        "时延敏感", "延迟敏感", "高速", "实时", "优先保证速度",
    ],
    "COST_CONSTRAINED": [
        "成本更低", "低成本", "便宜", "省钱", "节省预算",
        "最便宜", "费用低", "经济实惠",
    ],
    "LOAD_BALANCE": [
        "负载均衡", "资源竞争少", "不排队", "空闲资源",
        "高并发", "分布式",
    ],
}


def detect_routing_strategy(user_input: str) -> str:
    """从用户输入中检测路由策略，未检测到返回默认策略"""
    if not user_input:
        return DEFAULT_STRATEGY
    text = user_input.lower()
    # 优先检测 COST 和 LOAD_BALANCE（有明确策略意图）
    for kw in STRATEGY_KEYWORDS.get("COST_CONSTRAINED", []):
        if kw in text:
            return "COST_CONSTRAINED"
    for kw in STRATEGY_KEYWORDS.get("LOAD_BALANCE", []):
        if kw in text:
            return "LOAD_BALANCE"
    for kw in STRATEGY_KEYWORDS.get("TIME_CONSTRAINED", []):
        if kw in text:
            return "TIME_CONSTRAINED"
    return DEFAULT_STRATEGY


# ---------------------- 时间解析函数 ----------------------

def parse_start_time(user_input: str) -> int:
    """解析开始时间，返回毫秒时间戳"""
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


def parse_duration(user_input: str, business_type: str) -> int:
    """解析运行时长，返回毫秒"""
    pattern = r'(?:(\d+)\s*小时)?\s*(?:(\d+)\s*分钟)?\s*(?:(\d+)\s*秒)?'
    match = re.search(pattern, user_input)
    if not match:
        raise ValueError("无法解析运行时长")
    hours, minutes, seconds = match.groups(default="0")
    total_ms = int(hours) * 3600 * 1000 + int(minutes) * 60 * 1000 + int(seconds) * 1000

    # 从配置获取最低运行时长
    config = get_business_config(business_type)
    min_runtime = config.min_runtime_ms if config else 5 * 60 * 1000

    if total_ms < min_runtime:
        raise ValueError(f"运行时长必须大于等于 {min_runtime // 1000 // 60} 分钟")
    return total_ms


# ---------------------- 向后兼容的模块级常量 ----------------------
# 保留旧接口，指向配置类

# 视频分辨率可选值（向后兼容）
VIDEO_RESOLUTIONS = VideoInferenceConfig.VIDEO_RESOLUTIONS

# 向后兼容的参数列表（从配置获取）
VIDEO_KEY_PARAMS = BUSINESS_CONFIG_REGISTRY[BusinessType.VIDEO_INFERENCE].key_params
TRAIN_KEY_PARAMS = BUSINESS_CONFIG_REGISTRY[BusinessType.MODEL_TRAINING].key_params


def get_min_runtime_ms(business_type: str) -> int:
    """获取最低运行时长（毫秒）"""
    config = get_business_config(business_type)
    return config.min_runtime_ms if config else 5 * 60 * 1000


# ---------------------- 核心解析函数 ----------------------

def parse_intent_output(llm_text: str, state: Optional[State] = None, fill_dag: bool = True, validate_values: bool = True, user_input: str = "") -> State:
    """
    解析 LLM 输出为结构化状态

    Args:
        llm_text: LLM 原始输出
        state: 当前状态
        fill_dag: 是否填充 DAG
        validate_values: 是否校验参数值合法性（默认True），False时只检查参数是否存在
        user_input: 用户原始输入，用于策略检测
    """
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

    # 保存用户原始输入（用于策略检测，跨调用保留）
    if user_input and not state.original_input:
        state.original_input = user_input

    state.intent_result = json_res
    task_name = json_res.get("任务名称") or ""  # 原"业务类型"字段
    params = json_res.get("参数", {})

    # 从任务名称中提取业务类型（用于匹配配置）
    # 例如 "视频AI推理业务1" -> "视频AI推理", "模型训练实验" -> "模型训练"
    business_type = None
    for bt in BusinessType:
        if bt.value in task_name:
            business_type = bt.value
            break

    # 将顶层任务名称同步到params中，用于参数校验
    if task_name and "任务名称" not in params:
        params["任务名称"] = task_name

    # 获取业务配置
    config = get_business_config(business_type)

    # ---------------------- 参数名纠正 ----------------------
    # 通用参数名纠正（在业务类型判断之前应用）
    COMMON_PARAM_RENAME_MAP = {
        "训练轮数": "训练轮次",
        "轮数": "训练轮次",
        "n轮": "训练轮次",
    }
    for wrong_name, correct_name in COMMON_PARAM_RENAME_MAP.items():
        if wrong_name in params:
            params[correct_name] = params.pop(wrong_name)

    # 使用配置中的参数名纠正映射
    if config:
        for wrong_name, correct_name in config.param_rename_map.items():
            if wrong_name in params:
                params[correct_name] = params.pop(wrong_name)

    # 移除 LLM 输出为 null 的 key
    params = {k: v for k, v in params.items() if v is not None}

    # ---------------------- 分辨率格式标准化 ----------------------
    # 支持 4k/1080p/720p 等别名，自动转为 1920x1080 等标准格式
    if "分辨率" in params:
        from config.business_config import normalize_resolution
        params["分辨率"] = normalize_resolution(params["分辨率"])

    # ---------------------- 业务模态预设 ----------------------
    # 模态由系统预设，不依赖用户输入或LLM输出
    if config and "模态" not in params:
        params["模态"] = config.modality
        # 同步更新 intent_result，确保前端能获取到预设的模态
        state.intent_result["参数"] = params

    # ---------------------- 终端IP补全 ----------------------
    # 源终端和目的终端的IP地址由系统通过工具函数查询补全
    if config and config.business_type in (BusinessType.VIDEO_INFERENCE, BusinessType.MODEL_TRAINING):
        params = enrich_terminal_params(params)
        # 同步更新 intent_result
        state.intent_result["参数"] = params

    # ---------------------- 参数校验 ----------------------
    missing_params = []
    reason_params = []

    if config:
        # 使用配置进行参数校验
        for k in config.key_params:
            v = params.get(k)
            if v is None or v == "":
                missing_params.append(k)
            elif validate_values:
                # 只有开启校验时才检查参数值合法性
                is_valid, reason = config.validate_param(k, v, params)
                if not is_valid:
                    reason_params.append({"param": k, "reason": reason})

        # 特殊校验：训练完成时间必须与期望运行时间相同
        if validate_values and config.business_type == BusinessType.MODEL_TRAINING:
            run_time = params.get("期望运行时间")
            finish_time = params.get("训练完成时间")
            if run_time is not None and finish_time is not None and finish_time != run_time:
                # 检查是否已在reason_params中
                if not any(r["param"] == "训练完成时间" for r in reason_params):
                    reason_params.append({"param": "训练完成时间", "reason": "必须与期望运行时间相同"})

        # 特殊校验：源终端和目的终端不能相同
        if validate_values:
            src = params.get("源终端")
            dst = params.get("目的终端")
            if src and dst and src == dst:
                if not any(r["param"] == "目的终端" for r in reason_params):
                    reason_params.append({"param": "目的终端", "reason": "目的终端不能与源终端相同"})

    elif business_type:
        # 未知业务类型
        reason_params.append({"param": "任务名称", "reason": f"无法识别的业务类型: {business_type}"})
        if not business_type:
            missing_params.append("任务名称")
    else:
        missing_params.append("任务名称")

    state.missing_params = missing_params
    state.reason_params = reason_params
    state.stage = "ask_missing" if missing_params or reason_params else "complete"
    state.parse_success = (
        config is not None and
        len(missing_params) == 0 and
        len(reason_params) == 0
    )

    # ---------------------- 策略检测 ----------------------
    # 优先使用原始用户输入（跨 slot→followup 调用时保留）
    text_for_strategy = state.original_input or user_input
    detected_strategy = detect_routing_strategy(text_for_strategy)
    params["策略"] = detected_strategy

    # ---------------------- DAG 填充 ----------------------
    if fill_dag and state.parse_success and state.stage == "complete":
        if config and config.business_type == BusinessType.VIDEO_INFERENCE:
            dag_template = VideoInferenceDAG(session_id=state.session_id, policy_type=detected_strategy)
            start_time_str = params.get("开始时间")
            duration_str = params.get("期望运行时间")
            if start_time_str:
                dag_template.set_submit_ts_ms(parse_start_time(start_time_str))
            if duration_str:
                runtime_ms = parse_duration(duration_str, business_type)
                dag_template.set_runtime(runtime_ms)
            state.dag = dag_template.to_dict()

        elif config and config.business_type == BusinessType.MODEL_TRAINING:
            dag_template = ModelTrainingDAG(session_id=state.session_id, policy_type=detected_strategy)
            start_time_str = params.get("开始时间")
            duration_str = params.get("期望运行时间")
            if start_time_str:
                dag_template.set_submit_ts_ms(parse_start_time(start_time_str))
            if duration_str:
                runtime_ms = parse_duration(duration_str, business_type)
                dag_template.set_runtime(runtime_ms)
            state.dag = dag_template.to_dict()

    return state
