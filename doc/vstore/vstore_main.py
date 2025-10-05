"""
向量存储主类
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
import logging

logger = logging.getLogger(__name__)


class VectorStoreProvider(str, Enum):
    """向量存储提供商枚举"""
    REDIS = "redis"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    PGVECTOR = "pgvector"


class VectorStoreConfig(BaseModel):
    """向量存储配置"""
    provider: VectorStoreProvider = Field(..., description="向量存储提供商")
    collection_name: str = Field(..., min_length=1, description="集合名称")
    host: str = Field(default="localhost", description="主机地址")
    port: int = Field(gt=0, lt=65536, description="端口号")
    user: str = Field(default="", description="用户名")
    password: str = Field(default="", description="密码")
    embedding_model: str = Field(..., description="嵌入模型名称")
    top_k: int = Field(default=5, gt=0, le=100, description="返回结果数量")

    @field_validator('collection_name')
    @classmethod
    def validate_collection_name(cls, v: str) -> str:
        """验证集合名称格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("集合名称只能包含字母、数字、下划线和连字符")
        return v


class BaseVectorStore(ABC):
    """向量存储抽象基类"""

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档"""
        pass

    @abstractmethod
    def search(self, query: str) -> List[Document]:
        """搜索文档"""
        pass

    @abstractmethod
    def as_retriever(self) -> BaseRetriever:
        """获取检索器"""
        pass

    @abstractmethod
    def upsert_documents(self, documents: List[Document]) -> List[str]:
        """更新或插入文档"""
        pass


class VStoreMain:
    """向量存储主类"""

    def __init__(
        self,
        vector_store_provider: VectorStoreProvider,
        collection_name: str,
        host: str = "localhost",
        port: int = 6333,
        user: str = "",
        password: str = "",
        embedding_model: str = "text-embedding-v4",
        top_k: int = 5,
    ) -> None:
        """初始化向量存储

        Args:
            vector_store_provider: 向量存储提供商
            collection_name: 集合名称
            host: 主机地址
            port: 端口号
            user: 用户名
            password: 密码
            embedding_model: 嵌入模型
            top_k: 返回结果数量
        """
        # 验证配置
        self.config = VectorStoreConfig(
            provider=vector_store_provider,
            collection_name=collection_name,
            host=host,
            port=port,
            user=user,
            password=password,
            embedding_model=embedding_model,
            top_k=top_k,
        )

        self._vstore: Optional[BaseVectorStore] = None

    @property
    def vstore(self) -> BaseVectorStore:
        """懒加载向量存储实例"""
        if self._vstore is None:
            self._vstore = self._initialize_vstore()
        return self._vstore

    def _initialize_vstore(self) -> BaseVectorStore:
        """初始化向量存储客户端"""
        logger.info(f"初始化 {self.config.provider.value} 向量存储")

        match self.config.provider:
            case VectorStoreProvider.QDRANT:
                from doc.vstore.qdrant_vector_store_client import QdrantVectorStoreClient
                return QdrantVectorStoreClient(
                    collection_name=self.config.collection_name,
                    host=self.config.host,
                    port=self.config.port,
                    _user=self.config.user,
                    _password=self.config.password,
                    embedding_model=self.config.embedding_model,
                    top_k=self.config.top_k,
                )
            case VectorStoreProvider.REDIS:
                raise NotImplementedError("Redis 向量存储尚未实现")
            case VectorStoreProvider.MILVUS:
                raise NotImplementedError("Milvus 向量存储尚未实现")
            case VectorStoreProvider.PGVECTOR:
                raise NotImplementedError("Pgvector 向量存储尚未实现")
            case _:
                raise ValueError(f"不支持的向量存储提供商: {self.config.provider}")

    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档到向量存储

        Args:
            documents: 文档列表

        Returns:
            文档ID列表
        """
        if not documents:
            logger.warning("尝试添加空文档列表")
            return []

        logger.info(f"添加 {len(documents)} 个文档")
        return self.vstore.add_documents(documents)

    def search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """搜索相似文档

        Args:
            query: 查询文本
            k: 返回结果数量（可选，默认使用配置的top_k）

        Returns:
            相似文档列表
        """
        if not query.strip():
            raise ValueError("查询文本不能为空")

        # 临时覆盖top_k
        if k is not None and k != self.config.top_k:
            original_k = self.vstore.top_k
            self.vstore.top_k = k
            results = self.vstore.search(query)
            self.vstore.top_k = original_k
            return results

        return self.vstore.search(query)

    def as_retriever(self) -> BaseRetriever:
        """获取检索器对象"""
        return self.vstore.as_retriever()

    def upsert_documents(self, documents: List[Document]) -> List[str]:
        """更新或插入文档

        Args:
            documents: 文档列表

        Returns:
            文档ID列表
        """
        if not documents:
            logger.warning("尝试更新空文档列表")
            return []

        logger.info(f"更新/插入 {len(documents)} 个文档")
        return self.vstore.upsert_documents(documents)

    def __enter__(self) -> VStoreMain:
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        # 清理资源（如果需要）
        logger.info("关闭向量存储连接")
        self._vstore = None

    # def add_document(self, document: Document):
    #     self.vstore.add_document(document)

    # def search(self, query: str):
    #     return self.vstore.search(query)


if __name__ == "__main__":
    # from doc.loader.doc_loader import DocLoader
    # from doc.spliter.md_splitter import MdSplitter

    # loader = DocLoader(
    #     "url",
    #     [
    #         "https://lilianweng.github.io/posts/2023-06-23-agent/",  # AI代理相关文章
    #         # "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",  # 提示工程文章
    #         # "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",  # LLM对抗攻击文章
    #     ],
    # )
    # docs, error_urls = loader.load()
    # md_splitter = MdSplitter(
    #     headers=[
    #         ("#", "Header 1"),
    #         ("##", "Header 2"),
    #         ("###", "Header 3"),
    #         ("####", "Header 4"),
    #         ("#####", "Header 5"),
    #         ("######", "Header 6"),
    #     ],
    #     tokenizer_name="huggingface",
    #     encoding_name="Qwen/Qwen-7B-Chat",
    #     chunk_size=1000,
    #     chunk_overlap=200,
    #     keep_separator=True,
    # )
    # # md_splitter = MdSplitter(
    # #     headers=[
    # #         ("#", "Header 1"),
    # #         ("##", "Header 2"),
    # #         ("###", "Header 3"),
    # #         ("####", "Header 4"),
    # #         ("#####", "Header 5"),
    # #         ("######", "Header 6"),
    # #     ],
    # #     tokenizer_name="tiktoken",
    # #     encoding_name="cl100k_base",
    # #     chunk_size=1000,
    # #     chunk_overlap=200,
    # #     keep_separator=True,
    # # )
    # result = md_splitter.split(docs)
    vstore = VStoreMain(
        vector_store_provider=VectorStoreProvider.QDRANT,
        collection_name="document_store",
        host="localhost",
        port=6333,
        user="",
        password="",
        embedding_model="text-embedding-v4",
        top_k=3,
    )
    # ids = vstore.add_documents(result)
    # print(ids)
    search_result = vstore.search("什么是AI代理？")
    print(len(search_result))
    print(search_result[0].page_content)
