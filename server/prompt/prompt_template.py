# server/prompt/prompt_template.py
"""
业务提示词模板 - 从配置动态生成
"""

from config.business_config import (
    BUSINESS_CONFIG_REGISTRY,
    BusinessType,
    VideoInferenceConfig,
)


def _generate_video_inference_template() -> str:
    """生成视频AI推理业务模板"""
    config = BUSINESS_CONFIG_REGISTRY[BusinessType.VIDEO_INFERENCE]
    resolutions = VideoInferenceConfig.VIDEO_RESOLUTIONS

    return f"""视频AI推理业务参数模板
{{
  "任务名称": "视频AI推理",
  "参数": {{
      "模型名称": "yolov8",
      "延迟": "2",
      "视频帧率": "25",
      "分辨率": "1920x1080",
      "源终端": "终端h1",
      "目的终端": "终端h2",
      "开始时间": "2026-04-08 09:00",
      "期望运行时间": "45分钟"
  }}
}}
视频AI推理参数约束：
- 任务名称：业务类型标识，固定为"视频AI推理"，不可修改
- 模型名称：任意模型名均可
- 延迟：必须 >0 秒
- 视频帧率：必须 >0
- 分辨率：可选"{resolutions[0]}"、"{resolutions[1]}"、"{resolutions[2]}"
- 源终端：用户指定的视频流来源终端名称（如"终端h1"、"终端h2"等），系统会自动查询其IP地址
- 目的终端：用户指定的视频流目标终端名称（如"终端h3"、"终端h4"等），系统会自动查询其IP地址
- 开始时间：必须为有效日期时间格式 "YYYY-MM-DD HH:MM" 且不早于当前时间
- 期望运行时间：最短运行时间为{config.get_min_runtime_minutes()}分钟
- 模态：系统预设，无需用户输入，视频AI推理固定为"{config.modality}" """


def _generate_model_training_template() -> str:
    """生成模型训练业务模板"""
    config = BUSINESS_CONFIG_REGISTRY[BusinessType.MODEL_TRAINING]

    return f"""模型训练业务参数模板
{{
  "任务名称": "模型训练",
  "参数": {{
      "模型名称": "resnet",
      "数据集": "CIFAR-100",
      "训练轮次": "10",
      "开始时间": "2026-04-08 09:00",
      "期望运行时间": "1小时",
      "训练完成时间": "1小时"
  }}
}}
模型训练参数约束：
- 任务名称：业务类型标识，固定为"模型训练"，不可修改
- 模型名称：任意模型名均可
- 数据集：任意数据集名均可
- 训练轮次：必须为大于0的整数，支持"训练轮数"、"轮数"、"n轮"等表述
- 开始时间：必须为有效日期时间格式 "YYYY-MM-DD HH:MM" 且不早于当前时间
- 期望运行时间：最短运行时间为{config.get_min_runtime_minutes()}分钟
- 训练完成时间：必须与"期望运行时间"相同，如果用户说"期望完成时间"或"完成时间"，也映射到此参数
- 模态：系统预设，无需用户输入，模型训练固定为"{config.modality}" """


# 生成完整的业务模板字符串
BUSINESS_TEMPLATES = f"""
## 通用约束
- 所有参数值（包括数字）必须使用字符串格式，例如："2"、"25"、"10"
- 参数解析以解析函数反馈为准，允许用户灵活表述但不能编造

{_generate_video_inference_template()}

{_generate_model_training_template()}
"""
