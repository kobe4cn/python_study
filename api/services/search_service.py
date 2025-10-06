"""
搜索服务
处理向量搜索相关的业务逻辑
"""

from __future__ import annotations

import logging
import asyncio
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document

from api.config import settings
from api.dependencies import (
    get_vector_store,
    get_cached_data,
    set_cached_data
)

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务类"""

    def __init__(self):
        """初始化搜索服务"""
        self.use_cache = settings.redis_enabled

    async def search_documents(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_scores: bool = True,
        use_cache: bool = True
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        搜索文档

        Args:
            query: 查询文本
            collection_name: 集合名称
            top_k: 返回结果数量
            filter_metadata: 元数据过滤条件
            include_metadata: 是否包含元数据
            include_scores: 是否包含分数
            use_cache: 是否使用缓存

        Returns:
            (搜索结果列表, 耗时毫秒)
        """
        import time
        start_time = time.time()

        logger.info(f"搜索请求: query='{query[:50]}...', collection={collection_name}, top_k={top_k}")

        try:
            # 1. 尝试从缓存获取
            cache_key = None
            if use_cache and self.use_cache:
                cache_key = self._generate_cache_key(
                    query, collection_name, top_k, filter_metadata
                )
                cached_result = get_cached_data(cache_key)
                if cached_result:
                    logger.info(f"缓存命中: {cache_key}")
                    took_ms = (time.time() - start_time) * 1000
                    return json.loads(cached_result), took_ms

            # 2. 执行搜索 - 使用带分数的搜索方法
            vstore = get_vector_store(collection_name)

            if include_scores:
                # 使用similarity_search_with_score获取分数
                results_with_scores = await asyncio.to_thread(
                    vstore.vstore.similarity_search_with_score,
                    query,
                    k=top_k,
                    filter=filter_metadata
                )
            else:
                # 普通搜索
                docs = await asyncio.to_thread(
                    vstore.vstore.search,
                    query,
                    k=top_k,
                    filter_dict=filter_metadata
                )
                results_with_scores = [(doc, None) for doc in docs]

            # 3. 格式化结果
            formatted_results = []
            for doc, score in results_with_scores:
                # 从元数据获取真实的文档ID
                doc_id = doc.metadata.get("doc_id") or doc.metadata.get("id") or f"{collection_name}_{hash(doc.page_content) % 10000}"

                result_item = {
                    "doc_id": doc_id,
                    "content": doc.page_content,
                }

                if include_metadata:
                    result_item["metadata"] = doc.metadata

                if include_scores and score is not None:
                    result_item["score"] = float(score)

                formatted_results.append(result_item)

            # 4. 缓存结果
            if cache_key and self.use_cache:
                set_cached_data(cache_key, json.dumps(formatted_results))

            took_ms = (time.time() - start_time) * 1000
            logger.info(f"搜索完成: 找到 {len(formatted_results)} 个结果, 耗时 {took_ms:.2f}ms")

            return formatted_results, took_ms

        except Exception as e:
            logger.exception(f"搜索失败: {e}")
            raise

    async def search_with_scores(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        搜索文档并返回相似度分数

        Args:
            query: 查询文本
            collection_name: 集合名称
            top_k: 返回结果数量
            filter_metadata: 元数据过滤条件

        Returns:
            (带分数的搜索结果列表, 耗时毫秒)
        """
        import time
        start_time = time.time()

        try:
            vstore = get_vector_store(collection_name)

            # 使用带分数的搜索方法
            results_with_scores = await asyncio.to_thread(
                vstore.vstore.vector_store.similarity_search_with_score,
                query,
                k=top_k
            )

            # 格式化结果
            formatted_results = []
            for doc, score in results_with_scores:
                result_item = {
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                }
                formatted_results.append(result_item)

            took_ms = (time.time() - start_time) * 1000
            return formatted_results, took_ms

        except Exception as e:
            logger.exception(f"带分数搜索失败: {e}")
            raise

    async def batch_search(
        self,
        queries: List[str],
        collection_name: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[List[Dict[str, Any]]], float]:
        """
        批量搜索

        Args:
            queries: 查询列表
            collection_name: 集合名称
            top_k: 每个查询返回的结果数量
            filter_metadata: 元数据过滤条件

        Returns:
            (批量搜索结果列表, 总耗时毫秒)
        """
        import time
        start_time = time.time()

        logger.info(f"批量搜索: {len(queries)} 个查询")

        try:
            # 并发执行多个搜索
            tasks = [
                self.search_documents(
                    query=query,
                    collection_name=collection_name,
                    top_k=top_k,
                    filter_metadata=filter_metadata,
                    use_cache=True
                )
                for query in queries
            ]

            results = await asyncio.gather(*tasks)

            # 提取搜索结果（忽略单个查询的耗时）
            all_results = [result[0] for result in results]

            took_ms = (time.time() - start_time) * 1000
            logger.info(f"批量搜索完成: {len(queries)} 个查询, 总耗时 {took_ms:.2f}ms")

            return all_results, took_ms

        except Exception as e:
            logger.exception(f"批量搜索失败: {e}")
            raise

    async def semantic_search_with_rerank(
        self,
        query: str,
        collection_name: str,
        initial_k: int = 20,
        final_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        语义搜索 + 重排序（可选功能）

        Args:
            query: 查询文本
            collection_name: 集合名称
            initial_k: 初始检索数量
            final_k: 最终返回数量

        Returns:
            重排序后的搜索结果
        """
        # 1. 初始检索
        results, _ = await self.search_with_scores(
            query=query,
            collection_name=collection_name,
            top_k=initial_k
        )

        # 2. 这里可以添加重排序逻辑
        # 例如使用CrossEncoder或其他重排序模型
        # 简化版：直接按分数排序并截取
        sorted_results = sorted(
            results,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        return sorted_results[:final_k]

    def _generate_cache_key(
        self,
        query: str,
        collection_name: str,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> str:
        """
        生成缓存键

        Args:
            query: 查询文本
            collection_name: 集合名称
            top_k: 返回数量
            filter_metadata: 过滤条件

        Returns:
            缓存键
        """
        # 构建唯一标识
        cache_data = {
            "query": query,
            "collection": collection_name,
            "top_k": top_k,
            "filter": filter_metadata or {}
        }

        # 生成MD5哈希
        cache_str = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_str.encode()).hexdigest()

        return f"search:{collection_name}:{cache_hash}"

    async def get_similar_documents(
        self,
        document_id: str,
        collection_name: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        查找相似文档

        Args:
            document_id: 文档ID
            collection_name: 集合名称
            top_k: 返回数量

        Returns:
            相似文档列表
        """
        # 实现需要先获取文档内容，然后搜索
        # 这是一个简化版本
        logger.warning("get_similar_documents 功能待实现")
        return []


# 导出
__all__ = ["SearchService"]
