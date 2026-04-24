# test_dataset/templates.py
"""
测试数据集模板定义
使用占位符实现灵活的测试用例生成
"""

from typing import Dict, List

# 视频AI推理业务模板
VIDEO_INFERENCE_TEMPLATES = [
    # 模板1：完整参数
    "我想在{src_terminal}部署视频AI推理业务，使用{model}模型，延迟{latency}秒，帧率{framerate}，分辨率{resolution}，从{start_time}开始运行{duration}",
    # 模板2：缺少可选参数
    "帮我用{model}做视频推理业务，延迟{latency}秒，源终端{src_terminal}，目的终端{dst_terminal}",
    # 模板3：使用模型简称
    "部署视频AI推理业务，yolov8模型，延迟{latency}秒，源{src_terminal}，目的{dst_terminal}",
    # 模板4：简单表达
    "我想用{model}跑视频推理，{duration}",
    # 模板5：带开始时间
    "从{start_time}开始部署视频AI推理业务，模型是{model}，延迟{latency}秒",
]

# 模型训练业务模板
MODEL_TRAINING_TEMPLATES = [
    # 模板1：完整参数
    "我想训练{model}模型，使用{dataset}数据集，训练轮次{epochs}，从{start_time}开始运行{duration}",
    # 模板2：缺少可选参数
    "用{epochs}轮训练{model}，数据集是{dataset}",
    # 模板3：使用模型简称
    "跑一个模型训练任务，resnet50，cifar100，10轮",
    # 模板4：简单表达
    "训练{model}，数据集{dataset}，轮次{epochs}",
    # 模板5：带开始时间
    "从{start_time}开始训练{model}，数据集{dataset}，{epochs}轮",
]

# 槽位值域定义
SLOT_VALUES = {
    "model": [
        "yolov8", "resnet50", "resnet101", "vgg16", "mobilenet",
        "yolov5", "yolov7", "efficientnet", "vit", "bert",
    ],
    "latency": ["1", "2", "3", "5", "10"],
    "framerate": ["15", "24", "30", "60"],
    "resolution": ["720p", "1080p", "4k"],
    "src_terminal": ["h1", "h2", "h3", "终端h1", "终端h2", "终端h3"],
    "dst_terminal": ["h1", "h2", "h3", "终端h1", "终端h2", "终端h3"],
    "dataset": ["cifar100", "imagenet", "coco", "voc", "mnist"],
    "epochs": ["5", "10", "20", "30", "50", "100"],
    "start_time": ["2026-04-21 10:00", "2026-04-22 14:30", "2026-04-23 09:00"],
    "duration": ["30分钟", "1小时", "2小时", "30分钟", "3小时"],
}


def replace_slots(template: str, slot_dict: Dict[str, str]) -> str:
    """将模板中的占位符替换为具体值"""
    result = template
    for slot, value in slot_dict.items():
        result = result.replace(f"{{{slot}}}", value)
    return result


def generate_variations(template: str, slot_values: Dict[str, List[str]]) -> List[str]:
    """为单个模板生成所有可能的变体（笛卡尔积）"""
    import itertools

    # 找出模板中的所有槽位
    import re
    slots = re.findall(r"\{(\w+)\}", template)

    # 为每个槽位生成值列表
    value_lists = [slot_values.get(s, [s]) for s in slots]

    results = []
    for combination in itertools.product(*value_lists):
        slot_dict = dict(zip(slots, combination))
        results.append(replace_slots(template, slot_dict))

    return results


def get_all_templates() -> List[Dict]:
    """获取所有模板及其元数据"""
    return [
        {"type": "视频AI推理", "templates": VIDEO_INFERENCE_TEMPLATES},
        {"type": "模型训练", "templates": MODEL_TRAINING_TEMPLATES},
    ]