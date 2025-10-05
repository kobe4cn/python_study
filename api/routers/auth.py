"""
认证路由
处理JWT令牌的获取和刷新
"""

from __future__ import annotations

import logging
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from api.models.requests import TokenRequest, RefreshTokenRequest
from api.models.responses import TokenResponse
from api.security.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    authenticate_user
)
from api.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["认证"],
)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="获取访问令牌",
    description="使用用户名和密码获取JWT访问令牌"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    登录并获取访问令牌

    - **username**: 用户名
    - **password**: 密码

    返回访问令牌和刷新令牌
    """
    logger.info(f"登录请求: 用户={form_data.username}")

    # 认证用户
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        logger.warning(f"登录失败: 用户={form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user.get("role", "user")},
        expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(
        data={"sub": user["username"]}
    )

    logger.info(f"登录成功: 用户={form_data.username}")

    return TokenResponse(
        success=True,
        message="登录成功",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新访问令牌",
    description="使用刷新令牌获取新的访问令牌"
)
async def refresh_token(
    refresh_request: RefreshTokenRequest
):
    """
    刷新访问令牌

    - **refresh_token**: 刷新令牌

    返回新的访问令牌
    """
    logger.info("刷新令牌请求")

    try:
        # 验证刷新令牌
        payload = verify_token(refresh_request.refresh_token, token_type="refresh")

        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )

        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": username},
            expires_delta=access_token_expires
        )

        logger.info(f"令牌刷新成功: 用户={username}")

        return TokenResponse(
            success=True,
            message="令牌刷新成功",
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"令牌刷新失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌刷新失败"
        )


__all__ = ["router"]
