"""
搜索路由
处理文档搜索相关操作
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, status, Depends, Request
from api.models.requests import SearchRequest, BatchSearchRequest
from api.models.responses import SearchResponse, BatchSearchResponse, SearchResultItem
from api.services.search_service import SearchService
from api.security.auth import get_optional_user, require_permission
from api.middleware.rate_limit import limiter, get_search_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["搜索"],
)

# 搜索服务实例
search_service = SearchService()


@router.post(
    "",
    response_model=SearchResponse,
    summary="语义搜索",
    description="在指定集合中执行语义搜索"
)
@limiter.limit(get_search_rate_limit())
async def search_documents(
    request: Request,
    search_request: SearchRequest,
    current_user: dict = Depends(require_permission("search:execute"))
):
    """
    语义搜索文档 - 需要 search:execute 权限

    - **query**: 搜索查询文本
    - **collection_name**: 集合名称
    - **top_k**: 返回结果数量
    - **filter_metadata**: 元数据过滤条件（可选）

    普通用户只能搜索自己创建的文档，管理员可以搜索所有文档
    """
    logger.info(
        f"用户操作: {current_user['username']} 搜索文档 - "
        f"query='{search_request.query[:50]}...', k={search_request.top_k}"
    )

    try:
        # 如果不是管理员，添加创建者过滤条件
        filter_metadata = search_request.filter_metadata or {}
        if current_user.get("role") != "admin":
            filter_metadata["created_by"] = current_user["username"]
            logger.info(
                f"非管理员用户 {current_user['username']} 添加过滤条件: created_by"
            )

        results, took_ms = await search_service.search_documents(
            query=search_request.query,
            collection_name=search_request.collection_name,
            top_k=search_request.top_k,
            filter_metadata=filter_metadata,
            include_metadata=search_request.include_metadata,
            include_scores=search_request.include_scores
        )

        # 转换为响应格式
        search_results = [
            SearchResultItem(**result) for result in results
        ]

        return SearchResponse(
            success=True,
            query=search_request.query,
            results=search_results,
            total=len(search_results),
            took_ms=took_ms,
            collection_name=search_request.collection_name
        )

    except Exception as e:
        logger.exception(f"搜索失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/batch",
    response_model=BatchSearchResponse,
    summary="批量搜索",
    description="批量执行多个搜索查询"
)
@limiter.limit(get_search_rate_limit())
async def batch_search(
    request: Request,
    batch_request: BatchSearchRequest,
    current_user: dict = Depends(require_permission("search:execute"))
):
    """
    批量搜索 - 需要 search:execute 权限

    - **queries**: 查询列表（最多50个）
    - **collection_name**: 集合名称
    - **top_k**: 每个查询返回的结果数量

    普通用户只能搜索自己创建的文档，管理员可以搜索所有文档
    """
    logger.info(
        f"用户操作: {current_user['username']} 批量搜索 - "
        f"{len(batch_request.queries)} 个查询"
    )

    try:
        # 如果不是管理员，添加创建者过滤条件
        filter_metadata = batch_request.filter_metadata or {}
        if current_user.get("role") != "admin":
            filter_metadata["created_by"] = current_user["username"]
            logger.info(
                f"非管理员用户 {current_user['username']} 添加过滤条件: created_by"
            )

        all_results, took_ms = await search_service.batch_search(
            queries=batch_request.queries,
            collection_name=batch_request.collection_name,
            top_k=batch_request.top_k,
            filter_metadata=filter_metadata
        )

        # 构建响应
        search_responses = []
        for idx, (query, results) in enumerate(zip(batch_request.queries, all_results)):
            search_results = [SearchResultItem(**result) for result in results]
            search_responses.append(
                SearchResponse(
                    success=True,
                    query=query,
                    results=search_results,
                    total=len(search_results),
                    collection_name=batch_request.collection_name
                )
            )

        return BatchSearchResponse(
            success=True,
            message=f"批量搜索完成",
            results=search_responses,
            total_queries=len(batch_request.queries),
            took_ms=took_ms
        )

    except Exception as e:
        logger.exception(f"批量搜索失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


__all__ = ["router"]
