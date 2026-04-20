import json
import re
from typing import Optional
from datetime import datetime
import dateparser
from parser.state import State
from parser.dag_template import VideoInferenceDAG, ModelTrainingDAG


# 最低运行时长阈值：单位毫秒，按业务类型区分
MIN_RUNTIME_MS = {
    "视频AI推理": 5 * 60 * 1000,   # 5分钟
    "模型训练": 30 * 60 * 1000,    # 30分钟
}

VIDEO_KEY_PARAMS = ["模型名称", "延迟", "视频帧率", "分辨率", "开始时间", "期望运行时间"]
TRAIN_KEY_PARAMS = ["模型名称", "数据集", "训练轮次", "开始时间", "期望运行时间", "训练完成时间"]

# 视频分辨率可选值
VIDEO_RESOLUTIONS = ["1920x1080", "1280x720", "3840x2160"]


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


def parse_duration(user_input: str, business_type: str) -> int:
    pattern = r'(?:(\d+)\s*小时)?\s*(?:(\d+)\s*分钟)?\s*(?:(\d+)\s*秒)?'
    match = re.search(pattern, user_input)
    if not match:
        raise ValueError("无法解析运行时长")
    hours, minutes, seconds = match.groups(default="0")
    total_ms = int(hours) * 3600 * 1000 + int(minutes) * 60 * 1000 + int(seconds) * 1000
    min_runtime = MIN_RUNTIME_MS.get(business_type, 5 * 60 * 1000)
    if total_ms < min_runtime:
        raise ValueError(f"运行时长必须大于等于 {min_runtime//1000//60} 分钟")
    return total_ms


def parse_intent_output(llm_text: str, state: Optional[State] = None, fill_dag: bool = True) -> State:
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

    # ---------------------- 参数名纠正 ----------------------
    # LLM 可能返回近似参数名，自动纠正（灵活推断，不编造）
    param_rename_map = {
        "训练轮数": "训练轮次",
        "轮数": "训练轮次",
        "n轮": "训练轮次",
        "期望完成时间": "训练完成时间",
        "完成时间": "训练完成时间",
    }
    for wrong_name, correct_name in param_rename_map.items():
        if wrong_name in params:
            params[correct_name] = params.pop(wrong_name)

    # 移除 LLM 输出为 null 的 key
    params = {k: v for k, v in params.items() if v is not None}

    # ---------------------- 参数校验 ----------------------
    missing_params = []
    reason_params = []

    if business_type == "视频AI推理":
        for k in VIDEO_KEY_PARAMS:
            v = params.get(k)
            if v is None or v == "":
                missing_params.append(k)
            else:
                if k == "模型名称":
                    pass  # 无额外校验
                elif k == "延迟":
                    try:
                        if float(v) <= 0:
                            reason_params.append({"param": k, "reason": "必须大于0"})
                    except:
                        reason_params.append({"param": k, "reason": "必须为数字"})
                elif k == "视频帧率":
                    try:
                        if float(v) <= 0:
                            reason_params.append({"param": k, "reason": "必须大于0"})
                    except:
                        reason_params.append({"param": k, "reason": "必须为数字"})
                elif k == "分辨率":
                    # 支持多种格式：1920x1080, 1920*1080, 1920 1080, 1920X1080
                    normalized = re.sub(r'[\s*xX]', 'x', str(v).strip())
                    if not re.match(r'^\d+x\d+$', normalized):
                        reason_params.append({"param": k, "reason": f"格式应为 {'/'.join(VIDEO_RESOLUTIONS)}"})
                elif k == "开始时间":
                    try:
                        parse_start_time(v)
                    except Exception as e:
                        reason_params.append({"param": k, "reason": str(e)})
                elif k == "期望运行时间":
                    try:
                        parse_duration(v, business_type)
                    except Exception as e:
                        reason_params.append({"param": k, "reason": str(e)})

    elif business_type == "模型训练":
        for k in TRAIN_KEY_PARAMS:
            v = params.get(k)
            if v is None or v == "":
                missing_params.append(k)
            else:
                if k == "模型名称":
                    pass
                elif k == "数据集":
                    pass
                elif k == "训练轮次":
                    try:
                        if int(v) <= 0:
                            reason_params.append({"param": k, "reason": "必须大于0"})
                    except:
                        reason_params.append({"param": k, "reason": "必须为整数"})
                elif k == "开始时间":
                    try:
                        parse_start_time(v)
                    except Exception as e:
                        reason_params.append({"param": k, "reason": str(e)})
                elif k == "期望运行时间":
                    try:
                        parse_duration(v, business_type)
                    except Exception as e:
                        reason_params.append({"param": k, "reason": str(e)})
                elif k == "训练完成时间":
                    run_time = params.get("期望运行时间")
                    if run_time is not None and v != run_time:
                        reason_params.append({"param": k, "reason": "必须与期望运行时间相同"})
    else:
        reason_params.append({"param": "业务类型", "reason": f"未知业务类型: {business_type}"})
        if not business_type:
            missing_params.append("业务类型")

    state.missing_params = missing_params
    state.reason_params = reason_params
    state.stage = "ask_missing" if missing_params or reason_params else "complete"
    state.parse_success = (
        business_type in ["视频AI推理", "模型训练"] and
        len(missing_params) == 0 and
        len(reason_params) == 0
    )

    # ---------------------- DAG 填充 ----------------------
    if fill_dag and state.parse_success and state.stage == "complete":
        if business_type == "视频AI推理":
            dag_template = VideoInferenceDAG(session_id=state.session_id)
            start_time_str = params.get("开始时间")
            duration_str = params.get("期望运行时间")
            if start_time_str:
                dag_template.set_submit_ts_ms(parse_start_time(start_time_str))
            if duration_str:
                runtime_ms = parse_duration(duration_str, business_type)
                dag_template.set_runtime(runtime_ms)
            state.dag = dag_template.to_dict()

        elif business_type == "模型训练":
            dag_template = ModelTrainingDAG(session_id=state.session_id)
            start_time_str = params.get("开始时间")
            duration_str = params.get("期望运行时间")
            if start_time_str:
                dag_template.set_submit_ts_ms(parse_start_time(start_time_str))
            if duration_str:
                runtime_ms = parse_duration(duration_str, business_type)
                dag_template.set_runtime(runtime_ms)
            state.dag = dag_template.to_dict()

    return state
