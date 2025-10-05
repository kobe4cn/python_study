"""
安全中间件
安全头、CORS、请求验证
"""

from __future__ import annotations

import re
import logging
from typing import Callable, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from api.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全响应头中间件
    添加各种安全相关的HTTP头
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        添加安全头到响应

        Args:
            request: HTTP请求
            call_next: 下一个处理器

        Returns:
            带安全头的响应
        """
        response = await call_next(request)

        # 安全头配置
        security_headers = {
            # 防止点击劫持
            "X-Frame-Options": "DENY",
            # XSS保护
            "X-Content-Type-Options": "nosniff",
            # XSS过滤
            "X-XSS-Protection": "1; mode=block",
            # 严格传输安全（HSTS）- 仅在HTTPS时启用
            "Strict-Transport-Security": (
                "max-age=31536000; includeSubDomains" if settings.use_https else ""
            ),
            # 内容安全策略
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            # 引用者策略
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # 权限策略
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

        # 添加安全头
        for header, value in security_headers.items():
            if value:  # 只添加非空值
                response.headers[header] = value

        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    请求验证中间件
    验证请求的合法性，防止常见攻击
    """

    # 危险路径模式（路径遍历攻击）
    DANGEROUS_PATH_PATTERNS = [
        re.compile(r"\.\."),  # 父目录引用
        re.compile(r"//+"),  # 多斜杠
        re.compile(r"\\"),  # 反斜杠
    ]

    # SQL注入模式（基础检测）
    SQL_INJECTION_PATTERNS = [
        re.compile(
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            re.IGNORECASE,
        ),
        re.compile(r"(--|;|/\*|\*/|xp_|sp_)", re.IGNORECASE),
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        验证请求安全性

        Args:
            request: HTTP请求
            call_next: 下一个处理器

        Returns:
            响应或错误
        """
        # 1. 验证路径安全性
        path = str(request.url.path)
        for pattern in self.DANGEROUS_PATH_PATTERNS:
            if pattern.search(path):
                logger.warning(f"检测到危险路径模式: {path} from {request.client}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "error": "无效的请求路径"},
                )

        # 2. 验证查询参数（防止SQL注入等）
        query_string = str(request.url.query)
        if query_string:
            for pattern in self.SQL_INJECTION_PATTERNS:
                if pattern.search(query_string):
                    logger.warning(
                        f"检测到可疑的查询参数: {query_string[:100]} from {request.client}"
                    )
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"success": False, "error": "无效的查询参数"},
                    )

        # 3. 验证Content-Length（防止过大请求）
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > settings.max_upload_size:
                    logger.warning(f"请求体过大: {length} bytes from {request.client}")
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "success": False,
                            "error": f"请求体过大，最大允许 {settings.max_upload_size} 字节",
                        },
                    )
            except ValueError:
                pass

        # 4. 验证User-Agent（可选）
        user_agent = request.headers.get("user-agent", "")
        if not user_agent and settings.environment == "production":
            logger.warning(f"缺少User-Agent header from {request.client}")

        # 继续处理请求
        return await call_next(request)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    HTTPS重定向中间件
    将HTTP请求重定向到HTTPS
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """重定向HTTP到HTTPS"""

        if settings.use_https and request.url.scheme == "http":
            # 构建HTTPS URL
            https_url = request.url.replace(scheme="https")

            logger.info(f"重定向 HTTP -> HTTPS: {request.url} -> {https_url}")

            return JSONResponse(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": str(https_url)},
                content={"success": True, "message": "重定向到HTTPS"},
            )

        return await call_next(request)


def setup_cors(app: FastAPI) -> None:
    """
    配置CORS中间件

    Args:
        app: FastAPI应用实例
    """
    if not settings.cors_enabled:
        logger.info("CORS未启用")
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )

    logger.info(f"CORS已启用 - 允许的源: {', '.join(settings.cors_origins)}")


def setup_security_middleware(app: FastAPI) -> None:
    """
    设置所有安全相关中间件

    Args:
        app: FastAPI应用实例
    """
    # 1. CORS（最先添加）
    setup_cors(app)

    # 2. 安全头
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("安全头中间件已启用")

    # 3. 请求验证
    app.add_middleware(RequestValidationMiddleware)
    logger.info("请求验证中间件已启用")

    # 4. HTTPS重定向（如果启用）
    if settings.use_https:
        app.add_middleware(HTTPSRedirectMiddleware)
        logger.info("HTTPS重定向中间件已启用")

    # 5. Gzip压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("Gzip压缩中间件已启用")

    # 6. 可信主机（生产环境）
    if settings.environment == "production":
        trusted_hosts = ["*"]  # 根据实际情况配置
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
        logger.info(f"可信主机中间件已启用: {trusted_hosts}")


# 导出
__all__ = [
    "SecurityHeadersMiddleware",
    "RequestValidationMiddleware",
    "HTTPSRedirectMiddleware",
    "setup_cors",
    "setup_security_middleware",
]
