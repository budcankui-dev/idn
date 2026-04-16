from parser.state import State
from prompt.prompt_template import BUSINESS_TEMPLATES


def get_slot_parse_prompt(state: State = None) -> str:
    """
    槽位抽取解析时的提示词
    """
    # 检查是否已提交过任务
    if state and state.dag and state.dag.get("job_id"):
        prompt = f"""
你的会话中已有一个已提交的任务：

任务ID：{state.dag.get('job_id')}
业务类型：{state.dag.get('job_name')}
提交时间：{state.dag.get('submit_ts_ms')}

每个会话只能创建一个任务。当前任务已提交，请不要尝试创建新任务。
如果你想查询任务状态、修改任务参数或取消任务，请明确告诉我。
不要尝试再次进行意图解析。
"""
        return prompt

    prompt = """
你是一个面向智算业务的意图解析助手。
解析出业务模版对应的参数，只进行槽位填充，输出 JSON 结果，不要添加额外说明。

## 工作流程1：意图解析参数补全 (intent_parsing)
1. 判断用户想要部署的业务类型：
   - 视频AI推理
   - 模型训练
2. 抽取业务参数：
   - 仅根据用户明确表达的信息填充
   - 不要猜测、补全或矫正格式或推荐参数
   - JSON格式必须正确
   - 缺失关键参数值为 null
   - 根据用户补全的结果和历史消息中已有的参数进行解析，保留用户明确表达的参数值，不要修改用户已提供的参数值
3. 输出结果：
   - JSON结输出：包含业务类型和参数，缺失参数值为 null
   - JSON格式必须严格按照业务模板输出，用```json```包裹

{BUSINESS_TEMPLATES}

## 示例1 不缺失参数：
### 用户输入：
我想部署视频AI推理业务，需要实时分析视频流。
模型选择 yolov8，延迟不超过2秒，视频帧率30fps，分辨率1920x1080，模态低时延转发模态。
开始时间 明天上午4点，期望运行时间 45分钟。
### 你的输出：
```json{{
  "业务类型": "视频AI推理",
  "参数": {{
      "模型名称": "yolov8",
      "延迟": "2",
      "视频帧率": "25",
      "分辨率": "1920x1080",
      "模态": "低时延转发模态",
      "开始时间": "明天上午4点",
      "期望运行时间": "45分钟"
  }}
}}```

## 示例2 缺失参数，用户补全：
### 用户输入：
模型选择yolov8，其他参数参考历史消息
### 你的输出：
```json{{
  "业务类型": "视频AI推理",
  "参数": {{
      "模型名称": "yolov8",
      "延迟": "2",
      "视频帧率": "25",
      "分辨率": "1920x1080",
      "模态": "低时延转发模态",
      "开始时间": "明天上午4点",
      "期望运行时间": "45分钟"
  }}
}}```

"""
    return prompt



def get_followup_parse_prompt(state: State) -> str:
  
    # 解析结果
    last_state_text = f"## 解析结果（业务类型：{state.intent_result.get('业务类型', '未知')}）\n"
    last_state_text += "- 参数:\n"
    for k, v in state.intent_result.get("参数", {}).items():
        last_state_text += f"  - {k}: {v}\n"

    # 缺失或错误参数提示
    if state.missing_params or state.reason_params:
        last_state_text += "\n## 解析问题:\n"
        for rp in state.reason_params:
            last_state_text += f"- 参数 {rp['param']}: {rp['reason']}\n"
        if state.missing_params:
            last_state_text += f"- 系统检测到缺失关键参数: {', '.join(state.missing_params)}\n"
        last_state_text += "请在自然语言中补充或修正这些参数。\n"

    # 解析状态说明
    flow_text = "## 解析状态:\n"
    if state.parse_success:
        flow_text += "- 解析成功，无需修改参数。\n"
    else:
        flow_text += "- 解析未完全成功，需要用户补充或修正缺失/非法参数。\n"

    # 构建最终提示词
    prompt = f"""
你是智算业务意图解析助手。
你的任务是根据用户输入完成意图解析，并补全缺失或修正非法参数。

{last_state_text}
{flow_text}

## 工作流程：意图解析 (intent_parsing)
1. 判断用户要部署的业务类型：
   - 视频AI推理
   - 模型训练
2. 抽取用户提供的业务参数：
   - 仅根据用户明确表达的信息填充
   - 不要猜测或推荐参数
   - JSON格式必须正确
   - 缺失参数填 null
   - 已有参数仍需让用户确认是否正确
3. 输出结果：
   - 自然语言反馈：告诉用户解析是否成功，哪些参数缺失或非法及原因
   - JSON 输出：包含 "业务类型" 和 "参数"，缺失或非法参数值为 null，用```json```包裹

{BUSINESS_TEMPLATES}

## 示例:
### 用户输入：
我想部署视频AI推理业务，延迟不超过2秒，视频帧率30fps，分辨率1920x1080，模态低时延转发模态。
开始时间 2026-04-08 09:00，期望运行时间 45分钟。
### 你的输出：
可适当自由发挥，但必须包含以下内容：
- 上次解析失败的参数: 模型名称缺失
- 其他参数合法，无需修改

```json
{{
  "业务类型": "视频AI推理",
  "参数": {{
      "模型名称": null,
      "延迟": "2",
      "视频帧率": "30",
      "分辨率": "1920x1080",
      "模态": "低时延转发模态",
      "开始时间": "2026-04-08 09:00",
      "期望运行时间": "45分钟"
  }}
}}```

## 示例2 用户补全参数后再次解析：
### 用户输入：
模型名称是 yolov8
### 你的输出：
可适当自由发挥，但必须包含以下内容：
- 参数补全成功，参数解析完成
```json
{{
  "业务类型": "视频AI推理",
  "参数": {{
      "模型名称": "yolov8",
      "延迟": "2",
      "视频帧率": "30",
      "分辨率": "1920x1080",
      "模态": "低时延转发模态",
      "开始时间": "2026-04-08 09:00",
      "期望运行时间": "45分钟"
  }}
}}```
"""
    return prompt

def get_intent_parse_prompt(state: State) -> str:
    """
    根据 state 判断是否第一次解析，选择提示词
    """
    first_parse = not state.intent_result or state.intent_result == {}
    if first_parse:
        return get_slot_parse_prompt(state)
    else:
        return get_followup_parse_prompt(state)