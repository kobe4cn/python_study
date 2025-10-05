#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库表并初始化默认数据
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.database.models import Base
from api.database.session import init_db_engine, get_db_session, engine
from api.crud.user import user_crud
from api.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_tables():
    """创建所有数据库表"""
    logger.info("开始创建数据库表...")

    # 确保数据目录存在（用于SQLite）
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"数据库目录: {db_dir}")

    # 初始化引擎
    init_db_engine()

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    logger.info("✅ 数据库表创建完成")


def create_default_users():
    """创建默认用户"""
    logger.info("开始创建默认用户...")

    db = get_db_session()

    try:
        # 创建管理员用户
        admin_username = "admin"
        if not user_crud.get_by_username(db, admin_username):
            admin = user_crud.create(
                db,
                username=admin_username,
                email="admin@example.com",
                password="admin123",
                role="admin",
                permissions=["*"],
                full_name="系统管理员",
                is_superuser=True,
                created_by="system",
            )
            logger.info(f"✅ 创建管理员用户: {admin.username} (密码: admin123)")
        else:
            logger.info(f"⏭️  管理员用户已存在: {admin_username}")

        # 创建编辑者用户
        editor_username = "editor"
        if not user_crud.get_by_username(db, editor_username):
            editor = user_crud.create(
                db,
                username=editor_username,
                email="editor@example.com",
                password="editor123",
                role="editor",
                permissions=[
                    "document:create",
                    "document:read",
                    "document:update",
                    "document:delete",
                    "collection:read",
                    "search:execute",
                ],
                full_name="编辑者",
                created_by="system",
            )
            logger.info(f"✅ 创建编辑者用户: {editor.username} (密码: editor123)")
        else:
            logger.info(f"⏭️  编辑者用户已存在: {editor_username}")

        # 创建查看者用户
        viewer_username = "viewer"
        if not user_crud.get_by_username(db, viewer_username):
            viewer = user_crud.create(
                db,
                username=viewer_username,
                email="viewer@example.com",
                password="viewer123",
                role="viewer",
                permissions=["document:read", "search:execute"],
                full_name="查看者",
                created_by="system",
            )
            logger.info(f"✅ 创建查看者用户: {viewer.username} (密码: viewer123)")
        else:
            logger.info(f"⏭️  查看者用户已存在: {viewer_username}")

        logger.info("✅ 默认用户创建完成")

    except Exception as e:
        logger.error(f"❌ 创建默认用户失败: {e}")
        raise
    finally:
        db.close()


def drop_all_tables():
    """删除所有表（危险操作）"""
    logger.warning("⚠️  警告: 即将删除所有数据库表!")

    response = input("确认删除所有表? (yes/no): ")
    if response.lower() != "yes":
        logger.info("操作已取消")
        return

    init_db_engine()
    Base.metadata.drop_all(bind=engine)
    logger.info("✅ 所有表已删除")


def reset_database():
    """重置数据库（删除并重新创建）"""
    logger.info("开始重置数据库...")

    # 删除所有表
    drop_all_tables()

    # 重新创建表
    create_tables()

    # 创建默认用户
    create_default_users()

    logger.info("✅ 数据库重置完成")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument(
        "action",
        choices=["init", "reset", "drop"],
        help="操作类型: init(初始化), reset(重置), drop(删除所有表)",
    )

    args = parser.parse_args()

    logger.info(f"数据库URL: {settings.database_url}")

    try:
        if args.action == "init":
            create_tables()
            create_default_users()
            logger.info("🎉 数据库初始化成功!")

        elif args.action == "reset":
            reset_database()
            logger.info("🎉 数据库重置成功!")

        elif args.action == "drop":
            drop_all_tables()
            logger.info("🎉 数据库表删除成功!")

    except Exception as e:
        logger.error(f"❌ 操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
