"""
基于Qdrant的向量存储客户端
"""

from typing import List, cast, Any
import dotenv
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


dotenv.load_dotenv()


class QdrantVectorStoreClient:
    """基于Qdrant的向量存储客户端"""

    def __init__(
        self,
        collection_name: str,
        host: str,
        port: int,
        _user: str,
        _password: str,
        embedding_model: str,
        top_k: int,
    ):
        client = QdrantClient(host=host, port=port)
        self.embeddings = DashScopeEmbeddings(model=embedding_model)
        vector_size = len(self.embeddings.embed_query("sample text"))
        self.collection_name = collection_name
        if not client.collection_exists(self.collection_name):
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        self.vector_store = QdrantVectorStore(
            client=client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
        self.top_k = top_k

    def add_documents(self, documents: List[Document]):
        """添加文档到向量存储"""
        return self.vector_store.add_documents(documents)

    def search(self, query: str):
        """搜索相似文档"""
        return self.vector_store.similarity_search(query, k=self.top_k)

    def as_retriever(self):
        """获取检索器对象"""
        return self.vector_store.as_retriever(search_kwargs={"k": self.top_k})

    def delete_documents_by_metadata(self, metadata_filter: dict):
        """根据元数据删除文档

        Args:
            metadata_filter: 元数据过滤条件，例如 {"source": "path/to/file.md"}
        """

        conditions: list[Any] = []
        for key, value in metadata_filter.items():
            conditions.append(
                FieldCondition(key=f"metadata.{key}", match=MatchValue(value=value))
            )

        filter_condition = Filter(must=cast(Any, conditions))
        self.vector_store.client.delete(
            collection_name=self.collection_name, points_selector=filter_condition
        )

    def document_exists(self, metadata_filter: dict) -> bool:
        """检查符合元数据条件的文档是否存在

        Args:
            metadata_filter: 元数据过滤条件，例如 {"source": "path/to/file.md"}

        Returns:
            bool: 如果存在返回 True，否则返回 False
        """

        conditions: list[Any] = []
        for key, value in metadata_filter.items():
            conditions.append(
                FieldCondition(key=f"metadata.{key}", match=MatchValue(value=value))
            )

        filter_condition = Filter(must=cast(Any, conditions))
        results = self.vector_store.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_condition,
            limit=1,
        )

        return len(results[0]) > 0

    def upsert_documents(self, documents: List[Document]):
        """添加或更新文档。如果文档已存在（基于 source 元数据），先删除再添加

        Args:
            documents: 要添加的文档列表，每个文档应包含 metadata 中的 source 字段
        """
        for doc in documents:
            if "source" in doc.metadata:
                # 如果文档已存在，先删除
                if self.document_exists({"source": doc.metadata["source"]}):
                    self.delete_documents_by_metadata(
                        {"source": doc.metadata["source"]}
                    )

        # 添加新文档
        self.add_documents(documents)
