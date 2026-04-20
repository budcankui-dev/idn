# server/config/settings.py
"""
配置加载器 - 单例模式
从 settings.yaml 加载所有全局配置
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    username: str
    password: str
    name: str
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        """生成数据库连接URL"""
        from urllib.parse import quote_plus
        password_encoded = quote_plus(self.password)
        return f"mysql+pymysql://{self.username}:{password_encoded}@{self.host}:{self.port}/{self.name}?charset=utf8mb4"


@dataclass
class AuthConfig:
    """认证配置"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_hours: int = 168  # 7天


@dataclass
class AppConfig:
    """应用配置"""
    host: str = "0.0.0.0"
    port: int = 6000


class Settings:
    """配置管理类（单例模式）"""
    _instance: Optional['Settings'] = None

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "settings.yaml"
            )

        with open(config_path, 'r', encoding='utf-8') as f:
            self._data = yaml.safe_load(f)

        db_data = self._data.get('database', {})
        self.database = DatabaseConfig(
            host=db_data.get('host', 'localhost'),
            port=db_data.get('port', 3306),
            username=db_data.get('username', 'root'),
            password=db_data.get('password', ''),
            name=db_data.get('name', 'intent'),
            pool_size=db_data.get('pool_size', 10),
            max_overflow=db_data.get('max_overflow', 20),
        )

        auth_data = self._data.get('auth', {})
        self.auth = AuthConfig(
            secret_key=auth_data.get('secret_key', 'change-me'),
            algorithm=auth_data.get('algorithm', 'HS256'),
            access_token_expire_hours=auth_data.get('access_token_expire_hours', 168),
        )

        app_data = self._data.get('app', {})
        self.app = AppConfig(
            host=app_data.get('host', '0.0.0.0'),
            port=app_data.get('port', 6000),
        )

    @classmethod
    def get_instance(cls) -> 'Settings':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reload(cls) -> 'Settings':
        """重新加载配置"""
        cls._instance = cls()
        return cls._instance


def get_settings() -> Settings:
    """获取配置单例"""
    return Settings.get_instance()
