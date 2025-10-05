"""
日志中间件
记录请求和响应信息
"""

from __future__ import annotations

import time
import json
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI

from api.config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    记录所有HTTP请求的详细信息
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录日志

        Args:
            request: HTTP请求
            call_next: 下一个中间件/路由处理器

        Returns:
            HTTP响应
        """
        # 记录请求开始时间
        start_time = time.time()

        # 生成请求ID（从header获取或生成新的）
        request_id = request.headers.get(
            "X-Request-ID", f"req_{int(start_time * 1000)}"
        )

        # 记录请求信息
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }

        # 记录请求开始
        logger.info(f"请求开始: {request.method} {request.url.path}", extra=log_data)

        # 处理请求
        try:
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            # 记录响应信息
            log_data.update(
                {
                    "status_code": response.status_code,
                    "process_time": str(process_time),
                }
            )

            # 根据状态码选择日志级别
            if response.status_code >= 500:
                logger.error(
                    f"请求完成(错误): {request.method} {request.url.path} - {response.status_code}",
                    extra=log_data,
                )
            elif response.status_code >= 400:
                logger.warning(
                    f"请求完成(客户端错误): {request.method} {request.url.path} - {response.status_code}",
                    extra=log_data,
                )
            else:
                logger.info(
                    f"请求完成: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)",
                    extra=log_data,
                )

            return response

        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time

            # 记录异常
            log_data.update(
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time": str(process_time),
                }
            )

            logger.exception(
                f"请求异常: {request.method} {request.url.path}", extra=log_data
            )

            raise


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    结构化日志中间件
    以JSON格式记录所有请求
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录JSON格式日志"""

        start_time = time.time()
        request_id = request.headers.get(
            "X-Request-ID", f"req_{int(start_time * 1000)}"
        )

        # 构建日志数据
        log_entry = {
            "timestamp": time.time(),
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_string": str(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # 添加响应信息
            log_entry.update(
                {
                    "status_code": response.status_code,
                    "process_time_seconds": round(process_time, 4),
                    "success": response.status_code < 400,
                }
            )

            # 输出JSON日志
            if settings.log_format == "json":
                print(json.dumps(log_entry))
            else:
                logger.info(
                    f"{request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)"
                )

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            process_time = time.time() - start_time

            log_entry.update(
                {
                    "status_code": 500,
                    "process_time_seconds": round(process_time, 4),
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )

            if settings.log_format == "json":
                print(json.dumps(log_entry))
            else:
                logger.error(f"请求异常: {str(e)}")

            raise


def setup_logging_middleware(app: FastAPI) -> None:
    """
    为FastAPI应用设置日志中间件

    Args:
        app: FastAPI应用实例
    """
    if settings.log_format == "json":
        app.add_middleware(StructuredLoggingMiddleware)
        logger.info("已启用结构化日志中间件（JSON格式）")
    else:
        app.add_middleware(LoggingMiddleware)
        logger.info("已启用标准日志中间件")


# 导出
__all__ = [
    "LoggingMiddleware",
    "StructuredLoggingMiddleware",
    "setup_logging_middleware",
]
