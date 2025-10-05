"""
健康检查路由
提供系统健康状态和就绪检查端点
"""

from __future__ import annotations

import time
import logging
from fastapi import APIRouter, status
from api.models.responses import HealthResponse
from api.dependencies import check_qdrant_health, check_redis_health
from api.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["健康检查"])

# 记录启动时间
_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="健康检查",
    description="检查API服务和依赖服务的健康状态"
)
async def health_check():
    """
    健康检查端点

    返回:
    - API服务状态
    - 版本信息
    - 运行时间
    - 依赖服务状态（Qdrant、Redis等）
    """
    logger.debug("执行健康检查")

    # 计算运行时间
    uptime = time.time() - _start_time

    # 检查依赖服务
    dependencies = {}

    # 检查Qdrant
    try:
        qdrant_status = check_qdrant_health()
        dependencies["qdrant"] = qdrant_status
    except Exception as e:
        logger.error(f"Qdrant健康检查失败: {e}")
        dependencies["qdrant"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # 检查Redis（如果启用）
    if settings.redis_enabled:
        try:
            redis_status = check_redis_health()
            dependencies["redis"] = redis_status
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            dependencies["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }

    # 判断整体健康状态
    all_healthy = all(
        dep.get("status") in ["healthy", "disabled"]
        for dep in dependencies.values()
    )

    overall_status = "healthy" if all_healthy else "unhealthy"

    return HealthResponse(
        success=all_healthy,
        status=overall_status,
        version=settings.app_version,
        uptime_seconds=round(uptime, 2),
        dependencies=dependencies
    )


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="就绪检查",
    description="检查API是否准备好接受请求"
)
async def readiness_check():
    """
    就绪检查端点（用于Kubernetes等编排系统）

    返回200表示服务已准备好，否则返回503
    """
    logger.debug("执行就绪检查")

    try:
        # 检查关键依赖（Qdrant）
        qdrant_status = check_qdrant_health()

        if qdrant_status.get("status") == "healthy":
            return {
                "status": "ready",
                "message": "服务已就绪"
            }
        else:
            return {
                "status": "not_ready",
                "message": "依赖服务未就绪",
                "details": qdrant_status
            }, status.HTTP_503_SERVICE_UNAVAILABLE

    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        return {
            "status": "not_ready",
            "message": str(e)
        }, status.HTTP_503_SERVICE_UNAVAILABLE


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Ping",
    description="简单的ping端点"
)
async def ping():
    """简单的ping端点，用于快速检查服务是否运行"""
    return {"status": "ok", "message": "pong"}


__all__ = ["router"]
