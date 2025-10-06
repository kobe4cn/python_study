"""
基于Qdrant的向量存储客户端
"""

from __future__ import annotations

from typing import List, Optional, Any, Dict
from functools import lru_cache
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
import dotenv
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)
dotenv.load_dotenv()


class QdrantConfig(BaseModel):
    """Qdrant配置"""
    collection_name: str = Field(..., min_length=1)
    host: str = Field(default="localhost")
    port: int = Field(default=6333, gt=0, lt=65536)
    user: Optional[str] = None
    password: Optional[str] = None
    embedding_model: str = Field(default="text-embedding-v4")
    top_k: int = Field(default=5, gt=0, le=100)
    distance_metric: Distance = Field(default=Distance.COSINE)
    batch_size: int = Field(default=100, gt=0, le=500)


class QdrantVectorStoreClient:
    """基于Qdrant的向量存储客户端（优化版）"""

    def __init__(
        self,
        collection_name: str,
        host: str = "localhost",
        port: int = 6333,
        _user: str = "",
        _password: str = "",
        embedding_model: str = "text-embedding-v4",
        top_k: int = 5,
    ) -> None:
        """初始化Qdrant客户端

        Args:
            collection_name: 集合名称
            host: 主机地址
            port: 端口号
            _user: 用户名（可选）
            _password: 密码（可选）
            embedding_model: 嵌入模型
            top_k: 返回结果数量
        """
        self.config = QdrantConfig(
            collection_name=collection_name,
            host=host,
            port=port,
            user=_user if _user else None,
            password=_password if _password else None,
            embedding_model=embedding_model,
            top_k=top_k,
        )

        # 初始化客户端
        self._client: Optional[QdrantClient] = None
        self._embeddings: Optional[DashScopeEmbeddings] = None
        self._vector_store: Optional[QdrantVectorStore] = None

        # 延迟初始化
        self._initialize()

    @property
    def client(self) -> QdrantClient:
        """获取Qdrant客户端"""
        if self._client is None:
            raise RuntimeError("客户端未初始化")
        return self._client

    @property
    def embeddings(self) -> DashScopeEmbeddings:
        """获取嵌入模型"""
        if self._embeddings is None:
            raise RuntimeError("嵌入模型未初始化")
        return self._embeddings

    @property
    def vector_store(self) -> QdrantVectorStore:
        """获取向量存储"""
        if self._vector_store is None:
            raise RuntimeError("向量存储未初始化")
        return self._vector_store

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _initialize(self) -> None:
        """初始化客户端（带重试）"""
        try:
            # 创建客户端
            self._client = QdrantClient(
                host=self.config.host,
                port=self.config.port
            )

            # 初始化嵌入模型
            self._embeddings = DashScopeEmbeddings(
                model=self.config.embedding_model
            )

            # 获取向量维度
            vector_size = self._get_vector_size()

            # 确保集合存在
            self._ensure_collection_exists(vector_size)

            # 初始化向量存储
            self._vector_store = QdrantVectorStore(
                client=self._client,
                collection_name=self.config.collection_name,
                embedding=self._embeddings,
            )

            logger.info(f"Qdrant客户端初始化成功: {self.config.collection_name}")

        except Exception as e:
            logger.error(f"Qdrant客户端初始化失败: {e}")
            raise

    @lru_cache(maxsize=1)
    def _get_vector_size(self) -> int:
        """
        获取向量维度（缓存结果）

        优先从配置读取,仅在必要时调用嵌入服务
        避免初始化时依赖外部服务
        """
        # 优先从配置获取维度
        if hasattr(self.config, 'embedding_dimension') and self.config.embedding_dimension:
            logger.info(f"从配置获取向量维度: {self.config.embedding_dimension}")
            return self.config.embedding_dimension

        # 仅在必要时调用嵌入服务
        try:
            logger.info("调用嵌入服务获取向量维度")
            sample_text = "test"
            vector = self.embeddings.embed_query(sample_text)
            dimension = len(vector)
            logger.info(f"从嵌入服务获取向量维度: {dimension}")
            return dimension
        except Exception as e:
            logger.warning(f"无法从嵌入服务获取向量维度: {e}, 使用默认值1536")
            return 1536  # 默认维度(DashScope text-embedding-v3)

    def _ensure_collection_exists(self, vector_size: int) -> None:
        """确保集合存在"""
        if not self.client.collection_exists(self.config.collection_name):
            logger.info(f"创建集合: {self.config.collection_name}")
            self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=self.config.distance_metric
                ),
            )

    def add_documents(
        self,
        documents: List[Document],
        batch_size: Optional[int] = None
    ) -> List[str]:
        """批量添加文档

        Args:
            documents: 文档列表
            batch_size: 批处理大小（可选）

        Returns:
            文档ID列表
        """
        if not documents:
            return []

        batch_size = batch_size or self.config.batch_size
        ids: List[str] = []

        logger.info(f"添加 {len(documents)} 个文档，批大小: {batch_size}")

        # 分批处理
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                batch_ids = self.vector_store.add_documents(batch)
                ids.extend(batch_ids)
                logger.debug(f"已处理批次 {i//batch_size + 1}")
            except Exception as e:
                logger.error(f"批次 {i//batch_size + 1} 添加失败: {e}")
                raise

        return ids

    def search(
        self,
        query: str,
        k: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """搜索相似文档

        Args:
            query: 查询文本
            k: 返回数量
            filter_dict: 元数据过滤条件

        Returns:
            相似文档列表
        """
        k = k or self.config.top_k

        if filter_dict:
            # 构建过滤器
            qdrant_filter = self._build_filter(filter_dict)
            return self.vector_store.similarity_search(
                query,
                k=k,
                filter=qdrant_filter
            )

        return self.vector_store.similarity_search(query, k=k)

    def as_retriever(
        self,
        search_kwargs: Optional[Dict[str, Any]] = None
    ) -> BaseRetriever:
        """获取检索器对象

        Args:
            search_kwargs: 搜索参数

        Returns:
            检索器对象
        """
        kwargs = search_kwargs or {"k": self.config.top_k}
        return self.vector_store.as_retriever(search_kwargs=kwargs)

    def delete_documents_by_metadata(
        self,
        metadata_filter: Dict[str, Any]
    ) -> None:
        """根据元数据删除文档

        Args:
            metadata_filter: 元数据过滤条件
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector

        # 构建正确的Filter对象
        filter_obj = Filter(
            must=[
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
                for key, value in metadata_filter.items()
            ]
        )

        try:
            # 使用FilterSelector包装Filter对象
            self.client.delete(
                collection_name=self.config.collection_name,
                points_selector=FilterSelector(filter=filter_obj)
            )
            logger.info(f"删除文档成功: {metadata_filter}")
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            raise

    def document_exists(self, metadata_filter: Dict[str, Any]) -> bool:
        """检查文档是否存在

        Args:
            metadata_filter: 元数据过滤条件

        Returns:
            是否存在
        """
        filter_condition = self._build_filter(metadata_filter)

        try:
            results = self.client.scroll(
                collection_name=self.config.collection_name,
                scroll_filter=filter_condition,
                limit=1,
            )
            return len(results[0]) > 0
        except Exception as e:
            logger.error(f"检查文档存在性失败: {e}")
            return False

    def upsert_documents(
        self,
        documents: List[Document],
        batch_size: Optional[int] = None
    ) -> List[str]:
        """更新或插入文档

        Args:
            documents: 文档列表
            batch_size: 批处理大小

        Returns:
            文档ID列表
        """
        # 按source分组
        sources_to_delete = set()
        for doc in documents:
            if "source" in doc.metadata:
                sources_to_delete.add(doc.metadata["source"])

        # 删除已存在的文档
        for source in sources_to_delete:
            if self.document_exists({"source": source}):
                self.delete_documents_by_metadata({"source": source})

        # 添加新文档
        return self.add_documents(documents, batch_size)

    def _build_filter(self, metadata_filter: Dict[str, Any]) -> Filter:
        """构建Qdrant过滤器

        Args:
            metadata_filter: 元数据过滤字典

        Returns:
            Qdrant过滤器对象
        """
        conditions: List[FieldCondition] = []

        for key, value in metadata_filter.items():
            conditions.append(
                FieldCondition(
                    key=f"metadata.{key}",
                    match=MatchValue(value=value)
                )
            )

        return Filter(must=conditions)

    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息

        Returns:
            集合信息字典
        """
        try:
            info = self.client.get_collection(self.config.collection_name)
            return {
                "name": self.config.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            raise

    @property
    def top_k(self) -> int:
        """获取top_k配置"""
        return self.config.top_k

    @top_k.setter
    def top_k(self, value: int) -> None:
        """设置top_k配置"""
        self.config.top_k = value

    def __enter__(self) -> QdrantVectorStoreClient:
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        # 关闭连接
        if self._client:
            self._client.close()
            logger.info("Qdrant客户端连接已关闭")
