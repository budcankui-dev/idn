#!/usr/bin/env python
"""
数据库连接诊断脚本
用于测试MySQL连接和调试连接问题
"""

import sys
import socket
from urllib.parse import urlparse

# 数据库配置
DATABASE_URL = "mysql+pymysql://root:Bupt@1234@10.112.249.191:3306/intent?charset=utf8mb4"

def test_network_connectivity():
    """测试网络连接"""
    print("=" * 60)
    print("1. 测试网络连接")
    print("=" * 60)
    
    # 解析URL
    parsed = urlparse(f"mysql://{DATABASE_URL.split('://')[1]}")
    host = parsed.hostname
    port = parsed.port or 3306
    
    print(f"目标主机: {host}")
    print(f"目标端口: {port}")
    
    # 测试TCP连接
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✓ 可以连接到 {host}:{port}")
            return True
        else:
            print(f"✗ 无法连接到 {host}:{port}")
            print(f"  - 请检查 MySQL 服务是否在运行")
            print(f"  - 请检查防火墙设置")
            print(f"  - 请检查主机和端口是否正确")
            return False
    except socket.gaierror:
        print(f"✗ 无法解析主机名: {host}")
        return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False


def test_pymysql_connection():
    """测试 PyMySQL 连接"""
    print("\n" + "=" * 60)
    print("2. 测试 PyMySQL 连接")
    print("=" * 60)
    
    try:
        import pymysql
        print("✓ pymysql 已安装")
        
        # 解析连接参数
        parsed = urlparse(f"mysql://{DATABASE_URL.split('://')[1]}")
        host = parsed.hostname
        port = parsed.port or 3306
        username = parsed.username
        password = parsed.password
        database = parsed.path.lstrip('/')
        
        print(f"用户名: {username}")
        print(f"主机: {host}")
        print(f"端口: {port}")
        print(f"数据库: {database}")
        
        # 尝试连接
        conn = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database if database else None,
            charset='utf8mb4',
            connect_timeout=10
        )
        print("✓ PyMySQL 连接成功!")
        conn.close()
        return True
    except pymysql.err.OperationalError as e:
        print(f"✗ PyMySQL 操作错误: {e}")
        print("  - 可能是数据库不存在、用户名/密码错误或服务器不可达")
        return False
    except Exception as e:
        print(f"✗ PyMySQL 连接失败: {e}")
        return False


def test_sqlalchemy_connection():
    """测试 SQLAlchemy 连接"""
    print("\n" + "=" * 60)
    print("3. 测试 SQLAlchemy 连接")
    print("=" * 60)
    
    try:
        from sqlalchemy import create_engine, text
        
        print(f"连接字符串: {DATABASE_URL}")
        
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            connect_args={'connect_timeout': 10}
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ SQLAlchemy 连接成功!")
            return True
    except Exception as e:
        print(f"✗ SQLAlchemy 连接失败: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("MySQL 数据库连接诊断工具")
    print("=" * 60)
    
    # 运行测试
    test1 = test_network_connectivity()
    test2 = test_pymysql_connection()
    test3 = test_sqlalchemy_connection()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("诊断结果总结")
    print("=" * 60)
    print(f"网络连接: {'✓ 通过' if test1 else '✗ 失败'}")
    print(f"PyMySQL 连接: {'✓ 通过' if test2 else '✗ 失败'}")
    print(f"SQLAlchemy 连接: {'✓ 通过' if test3 else '✗ 失败'}")
    
    if test3:
        print("\n✓ 所有测试都通过，数据库连接正常!")
        return 0
    else:
        print("\n✗ 存在连接问题，请检查以下几点:")
        print("  1. MySQL 服务是否在运行? (ps aux | grep mysql)")
        print("  2. 主机地址和端口是否正确?")
        print("  3. 用户名和密码是否正确?")
        print("  4. 数据库是否存在?")
        print("  5. 防火墙是否允许连接?")
        print("  6. 网络是否可达 10.112.249.191:3306?")
        return 1


if __name__ == "__main__":
    sys.exit(main())
