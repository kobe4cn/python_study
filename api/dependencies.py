"""
FastAPI依赖注入
提供共享资源和服务实例
"""

from __future__ import annotations

from typing import Generator, Optional
from functools import lru_cache
import logging

from api.config import settings
from doc.vstore.vstore_main import VStoreMain, VectorStoreProvider
from doc.loader.doc_loader import DocLoader
from doc.spliter.md_splitter import MdSplitter

logger = logging.getLogger(__name__)


# ========== 向量存储依赖 ==========

@lru_cache()
def get_vector_store(
    collection_name: Optional[str] = None
) -> VStoreMain:
    """
    获取向量存储实例（单例模式）

    Args:
        collection_name: 集合名称（可选）

    Returns:
        VStoreMain实例
    """
    collection = collection_name or settings.qdrant_collection

    logger.debug(f"获取向量存储实例: {collection}")

    vstore = VStoreMain(
        vector_store_provider=VectorStoreProvider.QDRANT,
        collection_name=collection,
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        user=settings.qdrant_user,
        password=settings.qdrant_password,
        embedding_model=settings.embedding_model,
        top_k=settings.top_k,
    )

    return vstore


def get_vector_store_dependency(
    collection_name: Optional[str] = None
) -> Generator[VStoreMain, None, None]:
    """
    向量存储依赖（用于FastAPI依赖注入）

    Args:
        collection_name: 集合名称

    Yields:
        VStoreMain实例
    """
    vstore = get_vector_store(collection_name)
    try:
        yield vstore
    finally:
        # 清理资源（如果需要）
        pass


# ========== 文档处理依赖 ==========

def get_document_loader(
    doc_type: str = "file",
    doc_paths: list = None
) -> DocLoader:
    """
    获取文档加载器实例

    Args:
        doc_type: 文档类型（url/file）
        doc_paths: 文档路径列表

    Returns:
        DocLoader实例
    """
    doc_paths = doc_paths or []

    logger.debug(f"创建文档加载器: 类型={doc_type}, 路径数量={len(doc_paths)}")

    return DocLoader(
        doc_type=doc_type,
        doc_path=doc_paths
    )


def get_document_splitter(
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> MdSplitter:
    """
    获取文档分割器实例

    Args:
        chunk_size: 分块大小
        chunk_overlap: 分块重叠

    Returns:
        MdSplitter实例
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    logger.debug(f"创建文档分割器: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    return MdSplitter(
        headers=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5"),
            ("######", "Header 6"),
        ],
        tokenizer_name=settings.tokenizer_name,
        encoding_name=settings.encoding_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        keep_separator=True,
    )


# ========== Redis缓存依赖（可选） ==========

_redis_client = None


def get_redis_client():
    """
    获取Redis客户端（如果启用）

    Returns:
        Redis客户端或None
    """
    global _redis_client

    if not settings.redis_enabled:
        return None

    if _redis_client is None:
        try:
            import redis

            _redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # 测试连接
            _redis_client.ping()
            logger.info("Redis客户端连接成功")

        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            _redis_client = None

    return _redis_client


# ========== 缓存辅助函数 ==========

def get_cached_data(key: str) -> Optional[str]:
    """
    从缓存获取数据

    Args:
        key: 缓存键

    Returns:
        缓存的数据或None
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return None

    try:
        return redis_client.get(key)
    except Exception as e:
        logger.error(f"读取缓存失败: {e}")
        return None


def set_cached_data(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """
    设置缓存数据

    Args:
        key: 缓存键
        value: 缓存值
        ttl: 过期时间（秒）

    Returns:
        是否成功
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return False

    try:
        ttl = ttl or settings.cache_ttl
        redis_client.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.error(f"设置缓存失败: {e}")
        return False


def delete_cached_data(key: str) -> bool:
    """
    删除缓存数据

    Args:
        key: 缓存键

    Returns:
        是否成功
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return False

    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"删除缓存失败: {e}")
        return False


# ========== 健康检查依赖 ==========

def check_qdrant_health() -> dict:
    """
    检查Qdrant服务健康状态

    Returns:
        健康状态字典
    """
    try:
        import time
        start = time.time()

        vstore = get_vector_store()
        # 尝试获取集合信息
        info = vstore.vstore.get_collection_info()

        latency = (time.time() - start) * 1000  # 转换为毫秒

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "details": {
                "collection": info.get("name"),
                "vectors_count": info.get("vectors_count", 0)
            }
        }
    except Exception as e:
        logger.error(f"Qdrant健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def check_redis_health() -> dict:
    """
    检查Redis服务健康状态

    Returns:
        健康状态字典
    """
    if not settings.redis_enabled:
        return {
            "status": "disabled"
        }

    try:
        import time
        start = time.time()

        redis_client = get_redis_client()
        if redis_client is None:
            return {
                "status": "unhealthy",
                "error": "无法连接"
            }

        redis_client.ping()
        latency = (time.time() - start) * 1000

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        logger.error(f"Redis健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# 导出
__all__ = [
    "get_vector_store",
    "get_vector_store_dependency",
    "get_document_loader",
    "get_document_splitter",
    "get_redis_client",
    "get_cached_data",
    "set_cached_data",
    "delete_cached_data",
    "check_qdrant_health",
    "check_redis_health",
]
