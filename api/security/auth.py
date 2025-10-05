"""
认证依赖项
FastAPI依赖注入用于认证和授权
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import logging

from api.config import settings
from api.security.jwt import verify_token

logger = logging.getLogger(__name__)

# HTTP Bearer认证方案
security = HTTPBearer(auto_error=False)

# API密钥认证方案
api_key_header = APIKeyHeader(name=settings.api_key_header_name, auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Dict[str, Any]:
    """
    获取当前用户（通过JWT令牌）

    Args:
        credentials: HTTP认证凭据

    Returns:
        用户信息字典

    Raises:
        HTTPException: 认证失败
    """
    if credentials is None:
        logger.warning("未提供认证凭据")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # 验证令牌
        payload = verify_token(token, token_type="access")

        # 提取用户信息
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 这里可以从数据库加载完整的用户信息
        user_info = {
            "username": username,
            "role": payload.get("role", "user"),
            "permissions": payload.get("permissions", []),
        }

        logger.debug(f"用户认证成功: {username}")
        return user_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户认证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取当前活跃用户

    Args:
        current_user: 当前用户

    Returns:
        用户信息

    Raises:
        HTTPException: 用户被禁用
    """
    if current_user.get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用"
        )
    return current_user


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    验证API密钥

    Args:
        api_key: API密钥

    Returns:
        有效的API密钥

    Raises:
        HTTPException: API密钥无效
    """
    if api_key is None:
        logger.warning("未提供API密钥")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供API密钥",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # 检查API密钥是否有效
    # 获取API密钥列表并确保类型安全
    api_keys_list = settings.api_keys if isinstance(settings.api_keys, list) else []
    if not api_keys_list or api_key not in api_keys_list:
        logger.warning(f"无效的API密钥: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    logger.debug(f"API密钥验证成功: {api_key[:8]}...")
    return api_key


async def get_current_user_or_api_key(
    user: Optional[Dict[str, Any]] = Depends(get_current_user),
    api_key: Optional[str] = Depends(verify_api_key),
) -> Dict[str, Any]:
    """
    支持JWT或API密钥的灵活认证

    Args:
        user: 用户信息（通过JWT）
        api_key: API密钥

    Returns:
        认证信息

    Raises:
        HTTPException: 认证失败
    """
    # JWT认证优先
    if user:
        return user

    # API密钥认证
    if api_key:
        return {
            "username": "api_key_user",
            "role": "api",
            "api_key": api_key[:8] + "...",
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="需要JWT令牌或API密钥认证"
    )


def require_role(required_role: str):
    """
    要求特定角色的装饰器

    Args:
        required_role: 要求的角色

    Returns:
        依赖函数
    """

    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user),
    ) -> Dict[str, Any]:
        user_role = current_user.get("role", "user")
        if user_role != required_role and user_role != "admin":
            logger.warning(
                f"权限不足: 用户 {current_user.get('username')} "
                f"角色 {user_role}, 需要 {required_role}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 {required_role} 角色",
            )
        return current_user

    return role_checker


def require_permission(required_permission: str):
    """
    要求特定权限的装饰器

    Args:
        required_permission: 要求的权限

    Returns:
        依赖函数
    """

    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user),
    ) -> Dict[str, Any]:
        permissions = current_user.get("permissions", [])

        if required_permission not in permissions and "admin" not in permissions:
            logger.warning(
                f"权限不足: 用户 {current_user.get('username')} "
                f"需要权限 {required_permission}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要权限: {required_permission}",
            )
        return current_user

    return permission_checker


# 可选认证（不强制要求）
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[Dict[str, Any]]:
    """
    可选的用户认证（不强制）

    Args:
        credentials: HTTP认证凭据

    Returns:
        用户信息或None
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# 导出
__all__ = [
    "get_current_user",
    "get_current_active_user",
    "verify_api_key",
    "get_current_user_or_api_key",
    "require_role",
    "require_permission",
    "get_optional_user",
    "APIKeyHeader",
]
