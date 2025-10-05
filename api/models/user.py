"""
用户相关Pydantic模型
用于请求验证和响应序列化
"""

from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


# ========== 请求模型 ==========


class UserCreate(BaseModel):
    """创建用户请求"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: str = Field(default="viewer", description="角色")
    permissions: List[str] = Field(default_factory=list, description="权限列表")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("用户名只能包含字母、数字、下划线和连字符")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError("密码长度至少为6个字符")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"[0-9]", v):
            raise ValueError("密码必须包含数字")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """验证角色"""
        allowed_roles = ["admin", "editor", "viewer"]
        if v not in allowed_roles:
            raise ValueError(f"角色必须是以下之一: {', '.join(allowed_roles)}")
        return v


class UserUpdate(BaseModel):
    """更新用户请求"""

    email: Optional[EmailStr] = Field(None, description="邮箱")
    role: Optional[str] = Field(None, description="角色")
    permissions: Optional[List[str]] = Field(None, description="权限列表")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    is_active: Optional[bool] = Field(None, description="是否激活")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """验证角色"""
        if v is not None:
            allowed_roles = ["admin", "editor", "viewer"]
            if v not in allowed_roles:
                raise ValueError(f"角色必须是以下之一: {', '.join(allowed_roles)}")
        return v


class PasswordChange(BaseModel):
    """修改密码请求"""

    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        if len(v) < 6:
            raise ValueError("密码长度至少为6个字符")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"[0-9]", v):
            raise ValueError("密码必须包含数字")
        return v


class PasswordReset(BaseModel):
    """重置密码请求"""

    new_password: str = Field(..., min_length=6, description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        if len(v) < 6:
            raise ValueError("密码长度至少为6个字符")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"[0-9]", v):
            raise ValueError("密码必须包含数字")
        return v


class PermissionUpdate(BaseModel):
    """更新权限请求"""

    permissions: List[str] = Field(..., description="权限列表")


class RoleUpdate(BaseModel):
    """更新角色请求"""

    role: str = Field(..., description="角色")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """验证角色"""
        allowed_roles = ["admin", "editor", "viewer"]
        if v not in allowed_roles:
            raise ValueError(f"角色必须是以下之一: {', '.join(allowed_roles)}")
        return v


class UserActivate(BaseModel):
    """激活/禁用用户请求"""

    is_active: bool = Field(..., description="是否激活")


# ========== 响应模型 ==========


class UserResponse(BaseModel):
    """用户响应"""

    id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    is_active: bool
    is_superuser: bool
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    max_documents: int
    max_collections: int
    max_upload_size: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    created_by: Optional[str] = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """用户列表响应"""

    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserProfileResponse(BaseModel):
    """用户个人资料响应"""

    id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ========== 查询参数 ==========


class UserListParams(BaseModel):
    """用户列表查询参数"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    role: Optional[str] = Field(None, description="角色过滤")
    is_active: Optional[bool] = Field(None, description="激活状态过滤")
    search: Optional[str] = Field(None, description="搜索关键词")


# ========== 审计日志模型 ==========


class AuditLogResponse(BaseModel):
    """审计日志响应"""

    id: str
    user_id: str
    username: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""

    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
