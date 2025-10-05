"""
速率限制中间件
基于slowapi实现API速率限制
"""

from __future__ import annotations

import logging
from typing import Callable
from fastapi import FastAPI, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.config import settings

logger = logging.getLogger(__name__)


def get_identifier(request: Request) -> str:
    """
    获取请求标识符（用于速率限制）

    优先级:
    1. API密钥
    2. 用户身份（如果已认证）
    3. IP地址

    Args:
        request: HTTP请求

    Returns:
        唯一标识符
    """
    # 尝试从header获取API密钥
    api_key = request.headers.get(settings.api_key_header_name)
    if api_key:
        return f"apikey:{api_key}"

    # 尝试从认证信息获取用户
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1][:16]  # 使用token前16位作为标识
        return f"token:{token}"

    # 使用IP地址
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return get_remote_address(request)


# 创建Limiter实例
limiter = Limiter(
    key_func=get_identifier,
    default_limits=[settings.rate_limit_default] if settings.rate_limit_enabled else [],
    enabled=settings.rate_limit_enabled,
    headers_enabled=True,  # 在响应头中显示限制信息
)


def setup_rate_limiting(app: FastAPI) -> Limiter:
    """
    为FastAPI应用设置速率限制

    Args:
        app: FastAPI应用实例

    Returns:
        Limiter实例
    """
    if not settings.rate_limit_enabled:
        logger.info("速率限制未启用")
        return limiter

    # 添加异常处理器
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

    # 添加中间件
    app.add_middleware(SlowAPIMiddleware)

    logger.info(
        f"速率限制已启用 - 默认限制: {settings.rate_limit_default}, "
        f"上传限制: {settings.rate_limit_upload}, "
        f"搜索限制: {settings.rate_limit_search}"
    )

    return limiter


class CustomRateLimitMiddleware:
    """
    自定义速率限制中间件（可选的替代方案）
    """

    def __init__(self, app: FastAPI):
        self.app = app
        self.rate_limits: dict = {}

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """处理请求并应用速率限制"""

        if not settings.rate_limit_enabled:
            return await call_next(request)

        # 获取客户端标识
        client_id = get_identifier(request)

        # 这里可以实现自定义的速率限制逻辑
        # 例如：使用Redis存储计数器

        # 继续处理请求
        response = await call_next(request)

        return response


# 速率限制装饰器辅助函数
def get_upload_rate_limit() -> str:
    """获取文件上传速率限制"""
    return settings.rate_limit_upload if settings.rate_limit_enabled else "0/second"


def get_search_rate_limit() -> str:
    """获取搜索速率限制"""
    return settings.rate_limit_search if settings.rate_limit_enabled else "0/second"


def get_default_rate_limit() -> str:
    """获取默认速率限制"""
    return settings.rate_limit_default if settings.rate_limit_enabled else "0/second"


# 导出
__all__ = [
    "limiter",
    "setup_rate_limiting",
    "get_identifier",
    "get_upload_rate_limit",
    "get_search_rate_limit",
    "get_default_rate_limit",
]
