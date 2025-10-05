"""Pytest 配置文件"""

import pytest


def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line(
        "markers", "integration: 标记集成测试（需要网络连接或外部服务）"
    )
    config.addinivalue_line(
        "markers", "slow: 标记慢速测试"
    )
