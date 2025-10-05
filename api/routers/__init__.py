"""
API路由模块
"""

from api.routers.documents import router as documents_router
from api.routers.search import router as search_router
from api.routers.collections import router as collections_router
from api.routers.health import router as health_router
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.chat import router as chat_router

__all__ = [
    "documents_router",
    "search_router",
    "collections_router",
    "health_router",
    "auth_router",
    "users_router",
    "chat_router",
]
