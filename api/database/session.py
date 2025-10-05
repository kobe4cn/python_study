"""
数据库会话管理
提供数据库连接和会话管理功能
"""

from __future__ import annotations

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from api.config import settings

logger = logging.getLogger(__name__)

# 数据库引擎
engine = None
SessionLocal = None


def init_db_engine() -> None:
    """初始化数据库引擎"""
    global engine, SessionLocal

    if engine is not None:
        logger.warning("数据库引擎已经初始化")
        return

    try:
        # 创建数据库引擎
        engine = create_engine(
            settings.database_url,
            poolclass=QueuePool,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_pre_ping=True,  # 连接前检查连接是否有效
            pool_recycle=3600,  # 1小时后回收连接
            echo=settings.db_echo,  # SQL日志
        )

        # 创建会话工厂
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
        )

        logger.info(f"数据库引擎初始化成功: {settings.database_url}")

    except Exception as e:
        logger.error(f"数据库引擎初始化失败: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于FastAPI依赖注入

    Yields:
        Session: 数据库会话对象
    """
    if SessionLocal is None:
        init_db_engine()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    获取数据库会话（用于脚本）

    Returns:
        Session: 数据库会话对象
    """
    if SessionLocal is None:
        init_db_engine()

    return SessionLocal()


def close_db_engine() -> None:
    """关闭数据库引擎"""
    global engine

    if engine is not None:
        engine.dispose()
        logger.info("数据库引擎已关闭")
        engine = None
