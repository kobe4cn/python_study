"""
集合管理路由
处理向量存储集合的管理操作
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from qdrant_client import QdrantClient
from api.models.requests import CollectionCreateRequest
from api.models.responses import (
    CollectionResponse,
    CollectionListResponse,
    CollectionInfoResponse,
    MessageResponse
)
from api.dependencies import get_vector_store, check_qdrant_health
from api.security.auth import get_current_user, require_permission
from api.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/collections",
    tags=["集合管理"]
)


@router.get(
    "",
    response_model=CollectionListResponse,
    summary="列出所有集合",
    description="获取所有向量存储集合的列表"
)
async def list_collections(
    current_user: dict = Depends(require_permission("collection:read"))
):
    """列出所有集合 - 需要 collection:read 权限"""
    logger.info(f"用户操作: {current_user['username']} 获取集合列表")

    try:
        # 直接使用Qdrant客户端获取集合列表
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )

        collections = client.get_collections()

        collection_list = []
        for coll in collections.collections:
            collection_list.append(
                CollectionResponse(
                    success=True,
                    name=coll.name,
                    vectors_count=0,  # 需要额外查询
                    points_count=0
                )
            )

        return CollectionListResponse(
            success=True,
            message=f"找到 {len(collection_list)} 个集合",
            collections=collection_list,
            total=len(collection_list)
        )

    except Exception as e:
        logger.exception(f"获取集合列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{collection_name}/info",
    response_model=CollectionInfoResponse,
    summary="获取集合信息",
    description="获取指定集合的详细信息"
)
async def get_collection_info(
    collection_name: str,
    current_user: dict = Depends(require_permission("collection:read"))
):
    """获取集合详细信息 - 需要 collection:read 权限"""
    logger.info(
        f"用户操作: {current_user['username']} 获取集合信息 - {collection_name}"
    )

    try:
        vstore = get_vector_store(collection_name)
        info = vstore.vstore.get_collection_info()

        collection = CollectionResponse(
            success=True,
            name=info.get("name", collection_name),
            vectors_count=info.get("vectors_count", 0),
            points_count=info.get("points_count", 0),
            status=info.get("status", "unknown")
        )

        statistics = {
            "vectors_count": info.get("vectors_count", 0),
            "points_count": info.get("points_count", 0),
            "indexed_vectors_count": info.get("indexed_vectors_count", 0)
        }

        return CollectionInfoResponse(
            success=True,
            collection=collection,
            statistics=statistics
        )

    except Exception as e:
        logger.exception(f"获取集合信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{collection_name}",
    response_model=MessageResponse,
    summary="删除集合",
    description="删除指定的向量存储集合"
)
async def delete_collection(
    collection_name: str,
    current_user: dict = Depends(require_permission("collection:delete"))
):
    """删除集合 - 需要 collection:delete 权限"""
    logger.info(
        f"用户操作: {current_user['username']} 删除集合 - {collection_name}"
    )

    try:
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )

        client.delete_collection(collection_name)

        # 审计日志
        logger.info(
            f"审计日志: 用户 {current_user['username']} "
            f"删除集合成功 - {collection_name}"
        )

        return MessageResponse(
            success=True,
            message=f"集合 '{collection_name}' 已删除"
        )

    except Exception as e:
        logger.exception(f"删除集合失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


__all__ = ["router"]
