# server/config/business_config.py
"""
业务配置类 - 集中管理所有业务类型的参数定义、校验规则、默认值
参考 dag_template.py 的类设计模式
"""

import re
from enum import Enum
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field


class BusinessType(Enum):
    """业务类型枚举 - 类型安全"""
    VIDEO_INFERENCE = "视频AI推理"
    MODEL_TRAINING = "模型训练"


# ---------------------- 公共校验函数 ----------------------

def validate_positive_number(v) -> Tuple[bool, str]:
    """校验正数"""
    try:
        if float(v) <= 0:
            return False, "必须大于0"
        return True, ""
    except:
        return False, "必须为数字"


def validate_positive_int(v) -> Tuple[bool, str]:
    """校验正整数"""
    try:
        if int(v) <= 0:
            return False, "必须大于0"
        return True, ""
    except:
        return False, "必须为整数"


def validate_resolution(v, allowed_values: List[str]) -> Tuple[bool, str]:
    """校验分辨率格式"""
    # 支持多种格式：1920x1080, 1920*1080, 1920 1080, 1920X1080
    normalized = re.sub(r'[\s*xX]', 'x', str(v).strip())
    if not re.match(r'^\d+x\d+$', normalized):
        return False, f"格式应为 {'/'.join(allowed_values)}"
    return True, ""


# ---------------------- 配置类定义 ----------------------

@dataclass
class BusinessConfig:
    """
    业务配置基类
    统一管理某类业务的所有参数定义、校验规则、默认值
    """
    business_type: BusinessType
    key_params: List[str]                      # 必填参数名列表
    min_runtime_ms: int                        # 最低运行时长（毫秒）
    modality: str                              # 系统预设模态
    param_rename_map: Dict[str, str] = field(default_factory=dict)  # 参数名纠正映射
    param_specs: Dict[str, Dict] = field(default_factory=dict)      # 参数详细规格

    @property
    def value(self) -> str:
        """返回业务类型字符串值"""
        return self.business_type.value

    def get_min_runtime_minutes(self) -> int:
        """返回最低运行时长（分钟）"""
        return self.min_runtime_ms // 1000 // 60

    def get_param_spec(self, param_name: str) -> Optional[Dict]:
        """获取参数规格"""
        return self.param_specs.get(param_name)

    def normalize_param_name(self, name: str) -> Optional[str]:
        """参数名纠正 - 返回正确名称或None"""
        return self.param_rename_map.get(name)

    def validate_param(self, param_name: str, value, all_params: Dict = None) -> Tuple[bool, str]:
        """
        校验单个参数值
        返回 (is_valid, reason)
        """
        spec = self.param_specs.get(param_name)
        if spec is None:
            return True, ""  # 无规格定义，默认通过

        validation_fn = spec.get('validation')
        allowed_values = spec.get('allowed_values')

        # 校验函数优先
        if validation_fn:
            return validation_fn(value)

        # 校验可选值列表
        if allowed_values:
            if value not in allowed_values:
                return False, f"可选值: {', '.join(allowed_values)}"

        return True, ""


class VideoInferenceConfig(BusinessConfig):
    """视频AI推理业务配置"""

    VIDEO_RESOLUTIONS = ["1920x1080", "1280x720", "3840x2160"]

    def __init__(self):
        super().__init__(
            business_type=BusinessType.VIDEO_INFERENCE,
            key_params=["任务名称", "模型名称", "延迟", "视频帧率", "分辨率", "源终端", "目的终端", "开始时间", "期望运行时间"],
            min_runtime_ms=5 * 60 * 1000,  # 5分钟
            modality="低延时转发模态",
            param_rename_map={
                "训练轮数": "训练轮次",  # 不适用于视频，但保持兼容
                "轮数": "训练轮次",
                "n轮": "训练轮次",
            },
            param_specs={
                "模型名称": {
                    "validation": None,
                    "allowed_values": None,  # 任意模型名
                },
                "延迟": {
                    "validation": validate_positive_number,
                    "allowed_values": None,
                },
                "视频帧率": {
                    "validation": validate_positive_number,
                    "allowed_values": None,
                },
                "分辨率": {
                    "validation": lambda v: validate_resolution(v, self.VIDEO_RESOLUTIONS),
                    "allowed_values": self.VIDEO_RESOLUTIONS,
                },
                "开始时间": {
                    "validation": None,  # 动态校验，由parse_start_time处理
                    "allowed_values": None,
                },
                "期望运行时间": {
                    "validation": None,  # 动态校验，由parse_duration处理
                    "allowed_values": None,
                },
                "源终端": {
                    "validation": None,
                    "allowed_values": None,
                },
                "目的终端": {
                    "validation": None,
                    "allowed_values": None,
                },
            }
        )


class ModelTrainingConfig(BusinessConfig):
    """模型训练业务配置"""

    def __init__(self):
        super().__init__(
            business_type=BusinessType.MODEL_TRAINING,
            key_params=["任务名称", "模型名称", "数据集", "训练轮次", "源终端", "目的终端", "开始时间", "期望运行时间", "训练完成时间"],
            min_runtime_ms=30 * 60 * 1000,  # 30分钟
            modality="智算中心模态",
            param_rename_map={
                "期望完成时间": "训练完成时间",
                "完成时间": "训练完成时间",
            },
            param_specs={
                "模型名称": {
                    "validation": None,
                    "allowed_values": None,  # 任意模型名
                },
                "数据集": {
                    "validation": None,
                    "allowed_values": None,  # 任意数据集
                },
                "训练轮次": {
                    "validation": validate_positive_int,
                    "allowed_values": None,
                },
                "源终端": {
                    "validation": None,
                    "allowed_values": None,
                },
                "目的终端": {
                    "validation": None,
                    "allowed_values": None,
                },
                "开始时间": {
                    "validation": None,
                    "allowed_values": None,
                },
                "期望运行时间": {
                    "validation": None,
                    "allowed_values": None,
                },
                "训练完成时间": {
                    "validation": None,  # 特殊校验：需与期望运行时间相同
                    "allowed_values": None,
                },
            }
        )


# ---------------------- 配置注册表 ----------------------

BUSINESS_CONFIG_REGISTRY: Dict[BusinessType, BusinessConfig] = {
    BusinessType.VIDEO_INFERENCE: VideoInferenceConfig(),
    BusinessType.MODEL_TRAINING: ModelTrainingConfig(),
}


def get_business_config(business_type: str) -> Optional[BusinessConfig]:
    """
    根据业务类型字符串获取配置
    支持精确匹配和模糊匹配
    """
    # 精确匹配
    for bt, config in BUSINESS_CONFIG_REGISTRY.items():
        if bt.value == business_type:
            return config

    # 模糊匹配（兼容旧代码中可能的大小写差异等）
    business_type_lower = business_type.lower() if business_type else ""
    for bt, config in BUSINESS_CONFIG_REGISTRY.items():
        if bt.value.lower() == business_type_lower:
            return config

    return None


def get_all_business_types() -> List[str]:
    """获取所有业务类型字符串列表"""
    return [bt.value for bt in BusinessType]
