"""
测试配置管理模块
"""

import pytest
from core.config import (
    AppSettings,
    LLMSettings,
    VectorStoreSettings,
    DatabaseSettings,
    CacheSettings,
    SecuritySettings,
    DocumentSettings,
    ObservabilitySettings,
)


class TestLLMSettings:
    """测试LLM配置"""

    def test_default_values(self):
        """测试默认值"""
        settings = LLMSettings()
        assert settings.provider == "qwen"
        assert settings.model == "qwen3-max"
        assert settings.temperature == 0.5
        assert 0.0 <= settings.temperature <= 2.0

    def test_custom_values(self):
        """测试自定义值"""
        settings = LLMSettings(
            provider="openai",
            model="gpt-4",
            temperature=0.8,
            max_tokens=8000,
        )
        assert settings.provider == "openai"
        assert settings.model == "gpt-4"
        assert settings.temperature == 0.8
        assert settings.max_tokens == 8000

    def test_temperature_validation(self):
        """测试温度参数验证"""
        # 有效值
        settings = LLMSettings(temperature=0.0)
        assert settings.temperature == 0.0

        settings = LLMSettings(temperature=2.0)
        assert settings.temperature == 2.0

        # 无效值会在Pydantic验证时抛出ValidationError
        with pytest.raises(Exception):
            LLMSettings(temperature=3.0)


class TestVectorStoreSettings:
    """测试向量存储配置"""

    def test_default_values(self):
        """测试默认值"""
        settings = VectorStoreSettings()
        assert settings.store_type == "qdrant"
        assert settings.qdrant_host == "localhost"
        assert settings.qdrant_port == 6333
        assert settings.embedding_dimension == 1536

    def test_qdrant_configuration(self):
        """测试Qdrant配置"""
        settings = VectorStoreSettings(
            qdrant_host="vector-db.example.com",
            qdrant_port=6334,
            qdrant_collection="my_docs",
        )
        assert settings.qdrant_host == "vector-db.example.com"
        assert settings.qdrant_port == 6334
        assert settings.qdrant_collection == "my_docs"


class TestDatabaseSettings:
    """测试数据库配置"""

    def test_default_sqlite(self):
        """测试默认SQLite配置"""
        settings = DatabaseSettings()
        assert "sqlite" in settings.url

    def test_postgresql_url(self):
        """测试PostgreSQL URL"""
        settings = DatabaseSettings(
            url="postgresql://user:password@localhost:5432/dbname"
        )
        assert "postgresql" in settings.url
        assert settings.pool_size == 5

    def test_pool_configuration(self):
        """测试连接池配置"""
        settings = DatabaseSettings(
            pool_size=10, max_overflow=20, pool_timeout=60
        )
        assert settings.pool_size == 10
        assert settings.max_overflow == 20
        assert settings.pool_timeout == 60


class TestSecuritySettings:
    """测试安全配置"""

    def test_jwt_configuration(self):
        """测试JWT配置"""
        settings = SecuritySettings(
            secret_key="test-secret-key-minimum-32-characters-long",
            algorithm="HS256",
            access_token_expire_minutes=60,
        )
        assert len(settings.secret_key) >= 32
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 60

    def test_cors_configuration(self):
        """测试CORS配置"""
        settings = SecuritySettings(
            cors_enabled=True,
            cors_origins=["http://localhost:3000", "https://example.com"],
        )
        assert settings.cors_enabled
        assert len(settings.cors_origins) == 2


class TestDocumentSettings:
    """测试文档处理配置"""

    def test_chunk_configuration(self):
        """测试分块配置"""
        settings = DocumentSettings(chunk_size=1500, chunk_overlap=300)
        assert settings.chunk_size == 1500
        assert settings.chunk_overlap == 300

    def test_chunk_overlap_validation(self):
        """测试chunk_overlap验证"""
        # 有效:overlap < chunk_size
        settings = DocumentSettings(chunk_size=1000, chunk_overlap=200)
        assert settings.chunk_overlap < settings.chunk_size

        # 无效:overlap >= chunk_size
        with pytest.raises(Exception):
            DocumentSettings(chunk_size=1000, chunk_overlap=1000)

    def test_file_upload_configuration(self):
        """测试文件上传配置"""
        settings = DocumentSettings(
            max_upload_size=100 * 1024 * 1024,  # 100MB
            allowed_extensions=[".pdf", ".docx"],
        )
        assert settings.max_upload_size == 100 * 1024 * 1024
        assert ".pdf" in settings.allowed_extensions


class TestAppSettings:
    """测试应用主配置"""

    def test_default_configuration(self):
        """测试默认配置"""
        settings = AppSettings()
        assert settings.environment == "development"
        assert settings.port == 8000
        assert settings.workers == 4

    def test_environment_properties(self):
        """测试环境属性"""
        dev_settings = AppSettings(environment="development")
        assert dev_settings.is_development
        assert not dev_settings.is_production

        prod_settings = AppSettings(environment="production")
        assert prod_settings.is_production
        assert not prod_settings.is_development

    def test_nested_settings(self):
        """测试嵌套配置"""
        settings = AppSettings()

        # 验证子配置已初始化
        assert isinstance(settings.llm, LLMSettings)
        assert isinstance(settings.vector, VectorStoreSettings)
        assert isinstance(settings.database, DatabaseSettings)
        assert isinstance(settings.cache, CacheSettings)
        assert isinstance(settings.security, SecuritySettings)
        assert isinstance(settings.document, DocumentSettings)
        assert isinstance(settings.observability, ObservabilitySettings)

    def test_production_validation(self):
        """测试生产环境验证"""
        prod_settings = AppSettings(
            environment="production",
            debug=True,  # 不应在生产环境启用
            security_secret_key="your-secret-key-change-in-production",  # 默认key
        )

        warnings = prod_settings.validate_production_settings()
        assert len(warnings) > 0
        assert any("debug" in w.lower() for w in warnings)
        assert any("secret_key" in w.lower() for w in warnings)

    def test_get_llm_config(self):
        """测试获取LLM配置"""
        settings = AppSettings()
        llm_config = settings.get_llm_config()

        assert isinstance(llm_config, dict)
        assert "provider" in llm_config
        assert "model" in llm_config
        assert "temperature" in llm_config
