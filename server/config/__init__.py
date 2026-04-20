# server/config/__init__.py
"""
配置模块 - 集中管理所有配置
"""

from config.settings import get_settings, Settings
from config.business_config import (
    BusinessType,
    BusinessConfig,
    VideoInferenceConfig,
    ModelTrainingConfig,
    BUSINESS_CONFIG_REGISTRY,
    get_business_config,
)

__all__ = [
    "get_settings",
    "Settings",
    "BusinessType",
    "BusinessConfig",
    "VideoInferenceConfig",
    "ModelTrainingConfig",
    "BUSINESS_CONFIG_REGISTRY",
    "get_business_config",
]
