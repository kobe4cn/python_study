"""VStoreMain 单元测试"""

import pytest
from unittest.mock import Mock, patch
from doc.vstore.vstore_main import (
    VStoreMain,
    VectorStoreProvider,
    VectorStoreConfig,
    BaseVectorStore
)
from langchain_core.documents import Document


class TestVectorStoreProvider:
    """VectorStoreProvider 测试"""

    def test_enum_values(self):
        """测试枚举值"""
        assert VectorStoreProvider.QDRANT.value == "qdrant"
        assert VectorStoreProvider.REDIS.value == "redis"
        assert VectorStoreProvider.MILVUS.value == "milvus"
        assert VectorStoreProvider.PGVECTOR.value == "pgvector"

    def test_enum_string_comparison(self):
        """测试字符串比较"""
        assert VectorStoreProvider.QDRANT == "qdrant"


class TestVectorStoreConfig:
    """VectorStoreConfig 测试"""

    def test_config_validation(self):
        """测试配置验证"""
        config = VectorStoreConfig(
            provider=VectorStoreProvider.QDRANT,
            collection_name="test_collection",
            embedding_model="test-model"
        )
        assert config.provider == VectorStoreProvider.QDRANT
        assert config.collection_name == "test_collection"

    def test_invalid_collection_name(self):
        """测试无效的集合名称"""
        with pytest.raises(ValueError, match="集合名称只能包含"):
            VectorStoreConfig(
                provider=VectorStoreProvider.QDRANT,
                collection_name="invalid name!",  # 包含空格和特殊字符
                embedding_model="test-model"
            )

    def test_valid_collection_names(self):
        """测试有效的集合名称"""
        valid_names = ["test", "test_collection", "test-collection", "test123"]
        for name in valid_names:
            config = VectorStoreConfig(
                provider=VectorStoreProvider.QDRANT,
                collection_name=name,
                embedding_model="test-model"
            )
            assert config.collection_name == name

    def test_port_validation(self):
        """测试端口验证"""
        with pytest.raises(ValueError):
            VectorStoreConfig(
                provider=VectorStoreProvider.QDRANT,
                collection_name="test",
                port=70000,  # 超出范围
                embedding_model="test-model"
            )

    def test_top_k_validation(self):
        """测试top_k验证"""
        with pytest.raises(ValueError):
            VectorStoreConfig(
                provider=VectorStoreProvider.QDRANT,
                collection_name="test",
                top_k=0,  # 必须大于0
                embedding_model="test-model"
            )


class TestVStoreMain:
    """VStoreMain 测试"""

    def test_init(self):
        """测试初始化"""
        vstore = VStoreMain(
            vector_store_provider=VectorStoreProvider.QDRANT,
            collection_name="test_collection",
            embedding_model="test-model"
        )
        assert vstore.config.provider == VectorStoreProvider.QDRANT
        assert vstore._vstore is None  # 懒加载

    def test_unsupported_provider(self):
        """测试不支持的提供商"""
        vstore = VStoreMain(
            vector_store_provider=VectorStoreProvider.REDIS,
            collection_name="test",
            embedding_model="test-model"
        )
        with pytest.raises(NotImplementedError, match="Redis 向量存储尚未实现"):
            _ = vstore.vstore

    def test_add_documents_empty_list(self):
        """测试添加空文档列表"""
        with patch('doc.vstore.vstore_main.QdrantVectorStoreClient') as MockClient:
            vstore = VStoreMain(
                vector_store_provider=VectorStoreProvider.QDRANT,
                collection_name="test",
                embedding_model="test-model"
            )
            result = vstore.add_documents([])
            assert result == []

    def test_search_empty_query(self):
        """测试空查询"""
        with patch('doc.vstore.vstore_main.QdrantVectorStoreClient') as MockClient:
            vstore = VStoreMain(
                vector_store_provider=VectorStoreProvider.QDRANT,
                collection_name="test",
                embedding_model="test-model"
            )
            with pytest.raises(ValueError, match="查询文本不能为空"):
                vstore.search("")

    def test_context_manager(self):
        """测试上下文管理器"""
        with patch('doc.vstore.vstore_main.QdrantVectorStoreClient'):
            with VStoreMain(
                vector_store_provider=VectorStoreProvider.QDRANT,
                collection_name="test",
                embedding_model="test-model"
            ) as vstore:
                assert isinstance(vstore, VStoreMain)

    @patch('doc.vstore.vstore_main.QdrantVectorStoreClient')
    def test_lazy_loading(self, MockClient):
        """测试懒加载"""
        vstore = VStoreMain(
            vector_store_provider=VectorStoreProvider.QDRANT,
            collection_name="test",
            embedding_model="test-model"
        )
        # 初始化时不应该创建客户端
        assert vstore._vstore is None

        # 访问vstore属性时才创建
        _ = vstore.vstore
        MockClient.assert_called_once()
