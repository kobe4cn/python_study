"""
用户管理API路由
提供用户的增删改查等管理功能
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging
import math

from api.database import get_db
from api.crud.user import user_crud, audit_log_crud
from api.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserListParams,
    PasswordChange,
    PasswordReset,
    PermissionUpdate,
    RoleUpdate,
    UserActivate,
    UserProfileResponse,
    AuditLogListResponse,
)
from api.security.permissions import require_permission
from api.security.jwt import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["用户管理"])


def log_audit(
    db: Session,
    request: Request,
    user: dict,
    action: str,
    resource_type: str,
    resource_id: str = None,
    success: bool = True,
    error_message: str = None,
):
    """记录审计日志"""
    try:
        audit_log_crud.create(
            db,
            user_id=user.get("user_id", ""),
            username=user.get("username", ""),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=success,
            error_message=error_message,
        )
    except Exception as e:
        logger.error(f"审计日志记录失败: {e}")


# ========== 用户CRUD端点 ==========


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    创建新用户（仅管理员）

    - **username**: 用户名（3-50字符）
    - **email**: 邮箱
    - **password**: 密码（至少6字符，需包含字母和数字）
    - **role**: 角色（admin/editor/viewer）
    - **permissions**: 权限列表
    """
    try:
        user = user_crud.create(
            db,
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
            role=user_in.role,
            permissions=user_in.permissions,
            full_name=user_in.full_name,
            phone=user_in.phone,
            created_by=current_user["username"],
        )

        log_audit(
            db,
            request,
            current_user,
            "create_user",
            "user",
            user.id,
            success=True,
        )

        logger.info(f"用户创建成功: {user.username} by {current_user['username']}")
        return user

    except ValueError as e:
        log_audit(
            db,
            request,
            current_user,
            "create_user",
            "user",
            success=False,
            error_message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败",
        )


@router.get("/", response_model=UserListResponse)
async def list_users(
    params: UserListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    获取用户列表（仅管理员）

    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    - **role**: 角色过滤
    - **is_active**: 激活状态过滤
    - **search**: 搜索关键词（用户名/邮箱/姓名）
    """
    try:
        skip = (params.page - 1) * params.page_size

        users, total = user_crud.get_multi(
            db,
            skip=skip,
            limit=params.page_size,
            role=params.role,
            is_active=params.is_active,
            search=params.search,
        )

        total_pages = math.ceil(total / params.page_size) if total > 0 else 1

        return UserListResponse(
            users=users,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败",
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户信息"""
    try:
        user = user_crud.get(db, current_user["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    获取用户详情（仅管理员）

    - **user_id**: 用户ID
    """
    try:
        user = user_crud.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}",
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户详情失败",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    更新用户信息（仅管理员）

    - **user_id**: 用户ID
    - **email**: 邮箱（可选）
    - **role**: 角色（可选）
    - **permissions**: 权限列表（可选）
    - **full_name**: 全名（可选）
    - **phone**: 电话（可选）
    - **bio**: 个人简介（可选）
    - **avatar_url**: 头像URL（可选）
    - **is_active**: 是否激活（可选）
    """
    try:
        # 过滤None值
        update_data = {
            k: v for k, v in user_update.model_dump().items() if v is not None
        }

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供更新数据",
            )

        # 添加更新者信息
        update_data["updated_by"] = current_user["username"]

        user = user_crud.update(db, user_id=user_id, update_data=update_data)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}",
            )

        log_audit(
            db,
            request,
            current_user,
            "update_user",
            "user",
            user_id,
            success=True,
        )

        logger.info(f"用户更新成功: {user.username} by {current_user['username']}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户失败: {e}")
        log_audit(
            db,
            request,
            current_user,
            "update_user",
            "user",
            user_id,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    删除用户（仅管理员）

    - **user_id**: 用户ID
    """
    try:
        # 不允许删除自己
        if user_id == current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除自己",
            )

        success = user_crud.delete(db, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}",
            )

        log_audit(
            db,
            request,
            current_user,
            "delete_user",
            "user",
            user_id,
            success=True,
        )

        logger.info(f"用户删除成功: {user_id} by {current_user['username']}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        log_audit(
            db,
            request,
            current_user,
            "delete_user",
            "user",
            user_id,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败",
        )


# ========== 权限和角色管理 ==========


@router.put("/{user_id}/permissions", response_model=UserResponse)
async def update_user_permissions(
    user_id: str,
    permission_update: PermissionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    更新用户权限（仅管理员）

    - **user_id**: 用户ID
    - **permissions**: 权限列表
    """
    try:
        user = user_crud.update_permissions(
            db, user_id=user_id, permissions=permission_update.permissions
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}",
            )

        log_audit(
            db,
            request,
            current_user,
            "update_permissions",
            "user",
            user_id,
            success=True,
        )

        logger.info(
            f"用户权限更新成功: {user.username} by {current_user['username']}"
        )
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户权限失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户权限失败",
        )


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_update: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    更新用户角色（仅管理员）

    - **user_id**: 用户ID
    - **role**: 角色（admin/editor/viewer）
    """
    try:
        user = user_crud.update_role(db, user_id=user_id, role=role_update.role)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}",
            )

        log_audit(
            db,
            request,
            current_user,
            "update_role",
            "user",
            user_id,
            success=True,
        )

        logger.info(f"用户角色更新成功: {user.username} by {current_user['username']}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户角色失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户角色失败",
        )


# ========== 密码管理 ==========


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_change: PasswordChange,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    修改当前用户密码

    - **old_password**: 旧密码
    - **new_password**: 新密码（至少6字符，需包含字母和数字）
    """
    try:
        user = user_crud.get(db, current_user["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        # 验证旧密码
        if not user_crud.verify_password(
            password_change.old_password, user.hashed_password
        ):
            log_audit(
                db,
                request,
                current_user,
                "change_password",
                "user",
                user.id,
                success=False,
                error_message="旧密码错误",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误",
            )

        # 更新密码
        user_crud.update_password(db, user.id, password_change.new_password)

        log_audit(
            db,
            request,
            current_user,
            "change_password",
            "user",
            user.id,
            success=True,
        )

        logger.info(f"用户密码修改成功: {user.username}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败",
        )


@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_user_password(
    user_id: str,
    password_reset: PasswordReset,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    重置用户密码（仅管理员）

    - **user_id**: 用户ID
    - **new_password**: 新密码（至少6字符，需包含字母和数字）
    """
    try:
        user = user_crud.update_password(db, user_id, password_reset.new_password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}",
            )

        log_audit(
            db,
            request,
            current_user,
            "reset_password",
            "user",
            user_id,
            success=True,
        )

        logger.info(f"用户密码重置成功: {user.username} by {current_user['username']}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置密码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重置密码失败",
        )


# ========== 激活/禁用 ==========


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    激活用户（仅管理员）

    - **user_id**: 用户ID
    """
    try:
        user = user_crud.toggle_active(db, user_id=user_id, is_active=True)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}",
            )

        log_audit(
            db,
            request,
            current_user,
            "activate_user",
            "user",
            user_id,
            success=True,
        )

        logger.info(f"用户激活成功: {user.username} by {current_user['username']}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"激活用户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="激活用户失败",
        )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    禁用用户（仅管理员）

    - **user_id**: 用户ID
    """
    try:
        # 不允许禁用自己
        if user_id == current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用自己",
            )

        user = user_crud.toggle_active(db, user_id=user_id, is_active=False)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}",
            )

        log_audit(
            db,
            request,
            current_user,
            "deactivate_user",
            "user",
            user_id,
            success=True,
        )

        logger.info(f"用户禁用成功: {user.username} by {current_user['username']}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"禁用用户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="禁用用户失败",
        )


# ========== 审计日志 ==========


@router.get("/audit-logs/", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = 1,
    page_size: int = 20,
    user_id: str = None,
    action: str = None,
    resource_type: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("user:manage")),
):
    """
    获取审计日志列表（仅管理员）

    - **page**: 页码
    - **page_size**: 每页数量
    - **user_id**: 用户ID过滤
    - **action**: 操作过滤
    - **resource_type**: 资源类型过滤
    """
    try:
        skip = (page - 1) * page_size

        logs, total = audit_log_crud.get_multi(
            db,
            skip=skip,
            limit=page_size,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return AuditLogListResponse(
            logs=logs,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error(f"获取审计日志失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取审计日志失败",
        )
