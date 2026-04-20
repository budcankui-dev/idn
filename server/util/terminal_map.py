# server/util/terminal_map.py
"""
终端名称与IP映射关系工具函数
用于解析源终端和目的终端的IP地址
"""

from typing import Dict, Optional, Tuple


# Mock 终端名称到IP的映射表
_TERMINAL_MOCK_DB: Dict[str, str] = {
    "终端h1": "192.168.1.100",
    "终端h2": "192.168.1.101",
    "终端h3": "192.168.1.102",
    "终端h4": "192.168.1.103",
}


def get_terminal_ip(name: str) -> Optional[str]:
    """
    根据终端名称查询IP地址

    Args:
        name: 终端名称

    Returns:
        IP地址字符串，如果未找到返回None
    """
    return _TERMINAL_MOCK_DB.get(name)


def resolve_terminal_info(name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    解析终端信息，返回 (终端名称, IP地址)

    Args:
        name: 终端名称

    Returns:
        (终端名称, IP地址) 元组，如果未找到则返回 (name, None)
    """
    ip = get_terminal_ip(name)
    return (name, ip)


def enrich_terminal_params(params: dict) -> dict:
    """
    为参数字典中的源终端和目的终端补充IP地址

    Args:
        params: 包含"源终端"和"目的终端"的参数字典

    Returns:
        补充了"源终端IP"和"目的终端IP"的参数字典
    """
    result = dict(params)

    if "源终端" in result and result["源终端"]:
        src_name = result["源终端"]
        _, src_ip = resolve_terminal_info(src_name)
        result["源终端IP"] = src_ip

    if "目的终端" in result and result["目的终端"]:
        dst_name = result["目的终端"]
        _, dst_ip = resolve_terminal_info(dst_name)
        result["目的终端IP"] = dst_ip

    return result
