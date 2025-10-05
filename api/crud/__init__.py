"""
CRUD操作模块
提供数据库CRUD操作
"""

from api.crud.user import user_crud, audit_log_crud

__all__ = ["user_crud", "audit_log_crud"]
