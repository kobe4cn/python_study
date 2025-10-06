"""
API版本控制
支持URL路径版本和Header版本协商
"""

from __future__ import annotations

from typing import Optional, Callable
from enum import Enum
from fastapi import Request, HTTPException, status
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class APIVersionEnum(str, Enum):
    """API版本枚举"""

    V1 = "v1"
    V2 = "v2"


# 当前支持的版本
SUPPORTED_VERSIONS = [APIVersionEnum.V1]
LATEST_VERSION = APIVersionEnum.V1
DEPRECATED_VERSIONS: list[APIVersionEnum] = []


def get_api_version(request: Request) -> APIVersionEnum:
    """
    从请求中获取API版本

    优先级:
    1. URL路径中的版本 (/api/v1/...)
    2. Header中的版本 (X-API-Version: v1)
    3. 默认使用最新版本

    Args:
        request: FastAPI请求对象

    Returns:
        API版本

    Example:
        >>> version = get_api_version(request)
        >>> print(version)  # APIVersionEnum.V1
    """
    # 1. 从URL路径获取版本
    path = request.url.path
    for version in APIVersionEnum:
        if f"/{version.value}/" in path or path.endswith(f"/{version.value}"):
            return version

    # 2. 从Header获取版本
    version_header = request.headers.get("X-API-Version")
    if version_header:
        try:
            return APIVersionEnum(version_header.lower())
        except ValueError:
            logger.warning(f"Invalid API version in header: {version_header}")

    # 3. 返回最新版本
    return LATEST_VERSION


def validate_api_version(version: APIVersionEnum) -> None:
    """
    验证API版本是否支持

    Args:
        version: API版本

    Raises:
        HTTPException: 如果版本不支持或已弃用

    Example:
        >>> validate_api_version(APIVersionEnum.V1)  # OK
        >>> validate_api_version(APIVersionEnum.V2)  # 可能抛出异常
    """
    if version not in SUPPORTED_VERSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API version {version.value} is not supported. "
            f"Supported versions: {[v.value for v in SUPPORTED_VERSIONS]}",
        )

    if version in DEPRECATED_VERSIONS:
        logger.warning(
            f"API version {version.value} is deprecated and will be removed soon"
        )


def require_api_version(
    min_version: Optional[APIVersionEnum] = None,
    max_version: Optional[APIVersionEnum] = None,
):
    """
    装饰器:要求特定API版本范围

    Args:
        min_version: 最小版本(可选)
        max_version: 最大版本(可选)

    Example:
        >>> @app.get("/api/v1/users")
        >>> @require_api_version(min_version=APIVersionEnum.V1)
        >>> async def get_users(request: Request):
        ...     pass
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            version = get_api_version(request)
            validate_api_version(version)

            # 检查版本范围
            if min_version and version.value < min_version.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"This endpoint requires API version {min_version.value} or higher",
                )

            if max_version and version.value > max_version.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"This endpoint only supports API version up to {max_version.value}",
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def get_version_info() -> dict:
    """
    获取API版本信息

    Returns:
        版本信息字典

    Example:
        >>> info = get_version_info()
        >>> print(info["current"])  # "v1"
    """
    return {
        "current": LATEST_VERSION.value,
        "supported": [v.value for v in SUPPORTED_VERSIONS],
        "deprecated": [v.value for v in DEPRECATED_VERSIONS],
        "latest": LATEST_VERSION.value,
    }


# ==================== 版本迁移助手 ====================


class VersionMigration:
    """版本迁移助手

    提供版本间数据格式转换的工具

    Example:
        >>> migration = VersionMigration()
        >>> data_v2 = migration.migrate(data_v1, from_version="v1", to_version="v2")
    """

    @staticmethod
    def migrate(
        data: dict,
        from_version: str,
        to_version: str,
    ) -> dict:
        """
        在不同版本间迁移数据

        Args:
            data: 原始数据
            from_version: 源版本
            to_version: 目标版本

        Returns:
            迁移后的数据
        """
        if from_version == to_version:
            return data

        # TODO: 实现具体的版本迁移逻辑
        logger.info(f"Migrating data from {from_version} to {to_version}")

        return data


if __name__ == "__main__":
    print("=" * 60)
    print("API Versioning System")
    print("=" * 60)

    info = get_version_info()
    print(f"\nCurrent version: {info['current']}")
    print(f"Supported versions: {info['supported']}")
    print(f"Deprecated versions: {info['deprecated']}")
    print(f"Latest version: {info['latest']}")
