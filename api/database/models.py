"""
数据库模型定义
定义用户表和其他相关模型
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    Text,
    JSON,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# 创建基类
Base = declarative_base()


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    # 主键
    id = Column(String(36), primary_key=True, index=True)

    # 基本信息
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # 权限信息
    role = Column(String(50), default="viewer", nullable=False)
    permissions = Column(JSON, default=list, nullable=False)

    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # 个人信息
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)

    # 配额和限制
    max_documents = Column(Integer, default=1000, nullable=False)
    max_collections = Column(Integer, default=50, nullable=False)
    max_upload_size = Column(Integer, default=50 * 1024 * 1024, nullable=False)  # 50MB

    # 时间戳
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    # 审计信息
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}', role='{self.role}')>"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "phone": self.phone,
            "max_documents": self.max_documents,
            "max_collections": self.max_collections,
            "max_upload_size": self.max_upload_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }

    @property
    def has_admin_role(self) -> bool:
        """是否是管理员"""
        return self.role == "admin" or self.is_superuser

    def has_permission(self, permission: str) -> bool:
        """检查是否拥有指定权限"""
        if self.has_admin_role:
            return True

        # 检查通配符权限
        if "*" in self.permissions:
            return True

        return permission in self.permissions


class AuditLog(Base):
    """审计日志模型"""

    __tablename__ = "audit_logs"

    # 主键
    id = Column(String(36), primary_key=True, index=True)

    # 操作信息
    user_id = Column(String(36), index=True, nullable=False)
    username = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)

    # 详细信息
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # 结果信息
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog(username='{self.username}', action='{self.action}', resource='{self.resource_type}')>"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
