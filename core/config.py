"""
统一配置管理中心
使用Pydantic Settings进行配置验证和管理
支持多环境配置和配置验证
"""

from __future__ import annotations

import os
from typing import Dict, Any, List, Literal, Optional
from pathlib import Path
from functools import lru_cache

from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """LLM配置"""

    model_config = ConfigDict(env_prefix="LLM_", extra="ignore")

    # LLM提供商配置
    provider: Literal["qwen", "openai", "anthropic", "deepseek"] = Field(
        default="qwen", description="LLM提供商"
    )
    model: str = Field(default="qwen3-max", description="模型名称")
    api_key: str = Field(default="", description="API密钥")
    base_url: str = Field(default="", description="API基础URL")

    # 模型参数
    temperature: float = Field(default=0.5, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=4096, gt=0, le=32000, description="最大token数")
    stream: bool = Field(default=True, description="是否流式输出")

    # 超时和重试
    timeout: int = Field(default=60, gt=0, description="请求超时时间(秒)")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")


class VectorStoreSettings(BaseSettings):
    """向量存储配置"""

    model_config = ConfigDict(env_prefix="VECTOR_", extra="ignore")

    # 向量存储类型
    store_type: Literal["qdrant", "pinecone", "weaviate", "chroma"] = Field(
        default="qdrant", description="向量存储类型"
    )

    # Qdrant配置
    qdrant_host: str = Field(default="localhost", description="Qdrant主机地址")
    qdrant_port: int = Field(default=6333, gt=0, lt=65536, description="Qdrant端口")
    qdrant_collection: str = Field(default="documents", description="Qdrant集合名称")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API密钥")

    # 嵌入模型配置
    embedding_model: str = Field(
        default="text-embedding-v4", description="嵌入模型名称"
    )
    embedding_dimension: int = Field(
        default=1536, gt=0, le=4096, description="嵌入向量维度"
    )
    embedding_batch_size: int = Field(
        default=100, gt=0, le=1000, description="嵌入批处理大小"
    )


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    model_config = ConfigDict(env_prefix="DB_", extra="ignore")

    # 数据库连接
    url: str = Field(
        default="sqlite:///./data/app.db",
        description="数据库连接URL",
    )
    echo: bool = Field(default=False, description="是否输出SQL日志")

    # 连接池配置
    pool_size: int = Field(default=5, gt=0, le=50, description="连接池大小")
    max_overflow: int = Field(default=10, gt=0, le=100, description="连接池最大溢出")
    pool_timeout: int = Field(default=30, gt=0, description="连接池超时时间(秒)")
    pool_recycle: int = Field(
        default=3600, gt=0, description="连接回收时间(秒)"
    )


class CacheSettings(BaseSettings):
    """缓存配置"""

    model_config = ConfigDict(env_prefix="CACHE_", extra="ignore")

    # Redis配置
    enabled: bool = Field(default=False, description="是否启用缓存")
    backend: Literal["redis", "memory"] = Field(default="redis", description="缓存后端")

    redis_host: str = Field(default="localhost", description="Redis主机地址")
    redis_port: int = Field(default=6379, gt=0, lt=65536, description="Redis端口")
    redis_db: int = Field(default=0, ge=0, le=15, description="Redis数据库")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")

    # 缓存策略
    ttl: int = Field(default=300, gt=0, description="默认TTL(秒)")
    max_size: int = Field(default=1000, gt=0, description="内存缓存最大条目数")


class SecuritySettings(BaseSettings):
    """安全配置"""

    model_config = ConfigDict(env_prefix="SECURITY_", extra="ignore")

    # JWT配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32,
        description="JWT密钥",
    )
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(
        default=30, gt=0, description="访问令牌过期时间(分钟)"
    )
    refresh_token_expire_days: int = Field(
        default=7, gt=0, description="刷新令牌过期时间(天)"
    )

    # API密钥认证
    api_key_header_name: str = Field(default="X-API-Key", description="API密钥头名称")
    api_keys: List[str] = Field(default_factory=list, description="有效的API密钥列表")

    # CORS配置
    cors_enabled: bool = Field(default=True, description="启用CORS")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="允许的源",
    )


class DocumentSettings(BaseSettings):
    """文档处理配置"""

    model_config = ConfigDict(env_prefix="DOC_", extra="ignore")

    # 文件上传
    max_upload_size: int = Field(
        default=50 * 1024 * 1024, description="最大上传大小(字节)"
    )
    allowed_extensions: List[str] = Field(
        default=[".pdf", ".txt", ".md", ".doc", ".docx", ".html", ".json"],
        description="允许的文件扩展名",
    )
    upload_dir: Path = Field(default=Path("./uploads"), description="上传目录")

    # 文档分块
    chunk_size: int = Field(
        default=1000, gt=0, le=8000, description="文档分块大小(字符数)"
    )
    chunk_overlap: int = Field(
        default=200, ge=0, le=1000, description="文档分块重叠(字符数)"
    )

    # 检索配置
    top_k: int = Field(default=5, gt=0, le=100, description="检索返回数量")

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v: int, info) -> int:
        """验证chunk_overlap小于chunk_size"""
        chunk_size = info.data.get("chunk_size", 1000)
        if v >= chunk_size:
            raise ValueError(f"chunk_overlap ({v}) 必须小于 chunk_size ({chunk_size})")
        return v

    @field_validator("upload_dir")
    @classmethod
    def create_upload_dir(cls, v: Path) -> Path:
        """确保上传目录存在"""
        v.mkdir(parents=True, exist_ok=True)
        return v


class ObservabilitySettings(BaseSettings):
    """可观测性配置"""

    model_config = ConfigDict(env_prefix="OBSERVABILITY_", extra="ignore")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: Literal["json", "text"] = Field(default="json", description="日志格式")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")

    # Prometheus指标
    metrics_enabled: bool = Field(default=True, description="启用Prometheus指标")
    metrics_path: str = Field(default="/metrics", description="指标路径")

    # OpenTelemetry追踪
    tracing_enabled: bool = Field(default=False, description="启用分布式追踪")
    otel_service_name: str = Field(default="rag-system", description="服务名称")
    otel_exporter_endpoint: Optional[str] = Field(
        default=None, description="OTLP导出器端点"
    )


class AppSettings(BaseSettings):
    """应用主配置"""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用基础信息
    app_name: str = Field(default="RAG Document System", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="运行环境"
    )
    debug: bool = Field(default=False, description="调试模式")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器主机地址")
    port: int = Field(default=8000, gt=0, lt=65536, description="服务器端口")
    workers: int = Field(default=4, gt=0, le=32, description="工作进程数")
    reload: bool = Field(default=False, description="热重载")

    # TLS/SSL配置
    use_https: bool = Field(default=False, description="启用HTTPS")
    ssl_certfile: Optional[str] = Field(default=None, description="SSL证书文件路径")
    ssl_keyfile: Optional[str] = Field(default=None, description="SSL密钥文件路径")

    # 速率限制
    rate_limit_enabled: bool = Field(default=True, description="启用速率限制")
    rate_limit_default: str = Field(default="100/minute", description="默认速率限制")

    # 子配置
    llm: LLMSettings = Field(default_factory=LLMSettings)
    vector: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    document: DocumentSettings = Field(default_factory=DocumentSettings)
    observability: ObservabilitySettings = Field(
        default_factory=ObservabilitySettings
    )

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"

    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return self.database.url

    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置字典"""
        return self.llm.model_dump()

    def validate_production_settings(self) -> List[str]:
        """验证生产环境配置"""
        warnings = []

        if self.is_production:
            if self.debug:
                warnings.append("生产环境不应启用debug模式")

            if self.security.secret_key == "your-secret-key-change-in-production":
                warnings.append("生产环境必须修改默认secret_key")

            if not self.use_https:
                warnings.append("生产环境建议启用HTTPS")

            if self.llm.api_key == "":
                warnings.append("LLM API密钥未配置")

        return warnings


@lru_cache()
def get_settings() -> AppSettings:
    """
    获取应用配置单例
    使用lru_cache确保配置只加载一次
    """
    settings = AppSettings()

    # 验证生产环境配置
    if settings.is_production:
        warnings = settings.validate_production_settings()
        if warnings:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning("生产环境配置警告:")
            for warning in warnings:
                logger.warning(f"  - {warning}")

    return settings


# 全局配置实例
settings = get_settings()


if __name__ == "__main__":
    # 测试配置加载
    config = get_settings()

    print("=" * 60)
    print(f"应用名称: {config.app_name}")
    print(f"环境: {config.environment}")
    print(f"调试模式: {config.debug}")
    print("=" * 60)

    print("\nLLM配置:")
    print(f"  提供商: {config.llm.provider}")
    print(f"  模型: {config.llm.model}")
    print(f"  温度: {config.llm.temperature}")

    print("\n向量存储配置:")
    print(f"  类型: {config.vector.store_type}")
    print(f"  Qdrant地址: {config.vector.qdrant_host}:{config.vector.qdrant_port}")

    print("\n数据库配置:")
    print(f"  URL: {config.database.url}")
    print(f"  连接池大小: {config.database.pool_size}")

    print("\n安全配置:")
    print(f"  JWT算法: {config.security.algorithm}")
    print(f"  Token过期时间: {config.security.access_token_expire_minutes}分钟")

    # 检查生产环境配置
    if config.is_production:
        warnings = config.validate_production_settings()
        if warnings:
            print("\n⚠️  生产环境配置警告:")
            for warning in warnings:
                print(f"  - {warning}")
