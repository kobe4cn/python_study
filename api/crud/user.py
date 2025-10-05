"""
用户CRUD操作
提供用户的增删改查操作
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from passlib.context import CryptContext
import logging

from api.database.models import User, AuditLog

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD:
    """用户CRUD操作类"""

    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    def create(
        self,
        db: Session,
        *,
        username: str,
        email: str,
        password: str,
        role: str = "viewer",
        permissions: Optional[List[str]] = None,
        full_name: Optional[str] = None,
        created_by: Optional[str] = None,
        **kwargs: Any,
    ) -> User:
        """
        创建用户

        Args:
            db: 数据库会话
            username: 用户名
            email: 邮箱
            password: 密码
            role: 角色
            permissions: 权限列表
            full_name: 全名
            created_by: 创建者
            **kwargs: 其他字段

        Returns:
            创建的用户对象
        """
        # 检查用户名是否已存在
        if self.get_by_username(db, username=username):
            raise ValueError(f"用户名已存在: {username}")

        # 检查邮箱是否已存在
        if self.get_by_email(db, email=email):
            raise ValueError(f"邮箱已存在: {email}")

        # 创建用户对象
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            hashed_password=self.get_password_hash(password),
            role=role,
            permissions=permissions or [],
            full_name=full_name,
            created_by=created_by,
            **kwargs,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"用户创建成功: {username} (ID: {user.id})")
        return user

    def get(self, db: Session, user_id: str) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            db: 数据库会话
            email: 邮箱

        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.email == email).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[User], int]:
        """
        获取用户列表（带分页和过滤）

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            role: 角色过滤
            is_active: 激活状态过滤
            search: 搜索关键词（用户名或邮箱）

        Returns:
            (用户列表, 总数)
        """
        query = db.query(User)

        # 角色过滤
        if role:
            query = query.filter(User.role == role)

        # 激活状态过滤
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # 搜索过滤
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # 获取总数
        total = query.count()

        # 分页
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

        return users, total

    def update(
        self, db: Session, *, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[User]:
        """
        更新用户

        Args:
            db: 数据库会话
            user_id: 用户ID
            update_data: 更新数据

        Returns:
            更新后的用户对象或None
        """
        user = self.get(db, user_id)
        if not user:
            return None

        # 更新字段
        for field, value in update_data.items():
            if field == "password":
                # 密码需要加密
                setattr(user, "hashed_password", self.get_password_hash(value))
            elif hasattr(user, field):
                setattr(user, field, value)

        # 更新时间
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        logger.info(f"用户更新成功: {user.username} (ID: {user_id})")
        return user

    def delete(self, db: Session, user_id: str) -> bool:
        """
        删除用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        user = self.get(db, user_id)
        if not user:
            return False

        db.delete(user)
        db.commit()

        logger.info(f"用户删除成功: {user.username} (ID: {user_id})")
        return True

    def update_password(
        self, db: Session, user_id: str, new_password: str
    ) -> Optional[User]:
        """
        更新用户密码

        Args:
            db: 数据库会话
            user_id: 用户ID
            new_password: 新密码

        Returns:
            更新后的用户对象或None
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.hashed_password = self.get_password_hash(new_password)
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        logger.info(f"用户密码更新成功: {user.username} (ID: {user_id})")
        return user

    def update_permissions(
        self, db: Session, user_id: str, permissions: List[str]
    ) -> Optional[User]:
        """
        更新用户权限

        Args:
            db: 数据库会话
            user_id: 用户ID
            permissions: 权限列表

        Returns:
            更新后的用户对象或None
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.permissions = permissions
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        logger.info(f"用户权限更新成功: {user.username} (ID: {user_id})")
        return user

    def update_role(self, db: Session, user_id: str, role: str) -> Optional[User]:
        """
        更新用户角色

        Args:
            db: 数据库会话
            user_id: 用户ID
            role: 角色

        Returns:
            更新后的用户对象或None
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.role = role
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        logger.info(f"用户角色更新成功: {user.username} -> {role} (ID: {user_id})")
        return user

    def toggle_active(
        self, db: Session, user_id: str, is_active: bool
    ) -> Optional[User]:
        """
        切换用户激活状态

        Args:
            db: 数据库会话
            user_id: 用户ID
            is_active: 是否激活

        Returns:
            更新后的用户对象或None
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.is_active = is_active
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        status = "激活" if is_active else "禁用"
        logger.info(f"用户{status}成功: {user.username} (ID: {user_id})")
        return user

    def update_last_login(self, db: Session, user_id: str) -> Optional[User]:
        """
        更新用户最后登录时间

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            更新后的用户对象或None
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.last_login = datetime.utcnow()

        db.commit()
        db.refresh(user)

        return user

    def authenticate(
        self, db: Session, username: str, password: str
    ) -> Optional[User]:
        """
        认证用户

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            用户对象或None
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        # 更新最后登录时间
        self.update_last_login(db, user.id)

        return user


class AuditLogCRUD:
    """审计日志CRUD操作类"""

    def create(
        self,
        db: Session,
        *,
        user_id: str,
        username: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """
        创建审计日志

        Args:
            db: 数据库会话
            user_id: 用户ID
            username: 用户名
            action: 操作
            resource_type: 资源类型
            resource_id: 资源ID
            details: 详细信息
            ip_address: IP地址
            user_agent: User Agent
            success: 是否成功
            error_message: 错误信息

        Returns:
            审计日志对象
        """
        log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )

        db.add(log)
        db.commit()
        db.refresh(log)

        return log

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        success: Optional[bool] = None,
    ) -> tuple[List[AuditLog], int]:
        """
        获取审计日志列表

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            user_id: 用户ID过滤
            action: 操作过滤
            resource_type: 资源类型过滤
            success: 成功状态过滤

        Returns:
            (审计日志列表, 总数)
        """
        query = db.query(AuditLog)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if action:
            query = query.filter(AuditLog.action == action)

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if success is not None:
            query = query.filter(AuditLog.success == success)

        total = query.count()

        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

        return logs, total


# 创建全局实例
user_crud = UserCRUD()
audit_log_crud = AuditLogCRUD()
