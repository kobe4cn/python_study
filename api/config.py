"""
配置管理模块
使用Pydantic Settings进行环境变量管理
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import secrets

try:
    import json_log_formatter  # type: ignore
except ImportError:
    json_log_formatter = None


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # ========== 应用基础配置 ==========
    app_name: str = Field(default="文档管理API", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="production", description="运行环境")

    # ========== API配置 ==========
    api_v1_prefix: str = Field(default="/api/v1", description="API v1前缀")
    api_title: str = Field(default="文档管理API", description="API标题")
    api_description: str = Field(
        default="基于FastAPI的生产级文档管理系统", description="API描述"
    )

    # ========== 服务器配置 ==========
    host: str = Field(default="0.0.0.0", description="服务器主机地址")
    port: int = Field(default=8000, gt=0, lt=65536, description="服务器端口")
    workers: int = Field(default=4, gt=0, le=32, description="工作进程数")
    reload: bool = Field(default=False, description="热重载")

    # ========== TLS/SSL配置 ==========
    use_https: bool = Field(default=False, description="启用HTTPS")
    ssl_certfile: Optional[str] = Field(default=None, description="SSL证书文件路径")
    ssl_keyfile: Optional[str] = Field(default=None, description="SSL密钥文件路径")
    ssl_ca_certs: Optional[str] = Field(default=None, description="CA证书文件路径")
    ssl_cert_reqs: int = Field(default=0, description="SSL证书验证要求")

    # ========== CORS配置 ==========
    cors_enabled: bool = Field(default=True, description="启用CORS")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="允许的源",
    )
    cors_allow_credentials: bool = Field(default=True, description="允许凭据")
    cors_allow_methods: List[str] = Field(default=["*"], description="允许的方法")
    cors_allow_headers: List[str] = Field(default=["*"], description="允许的头部")

    # ========== 安全配置 ==========
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32), description="JWT密钥"
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
    api_keys: List[str] = Field(default=[], description="有效的API密钥列表")

    # ========== 速率限制配置 ==========
    rate_limit_enabled: bool = Field(default=True, description="启用速率限制")
    rate_limit_default: str = Field(default="100/minute", description="默认速率限制")
    rate_limit_upload: str = Field(default="10/minute", description="文件上传速率限制")
    rate_limit_search: str = Field(default="50/minute", description="搜索速率限制")

    # ========== 文件上传配置 ==========
    max_upload_size: int = Field(
        default=50 * 1024 * 1024, description="最大上传大小(50MB)"
    )
    allowed_file_types: List[str] = Field(
        default=[
            "application/pdf",
            "text/plain",
            "text/markdown",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/html",
            "application/json",
        ],
        description="允许的文件类型",
    )
    allowed_file_extensions: List[str] = Field(
        default=[".pdf", ".txt", ".md", ".doc", ".docx", ".html", ".json"],
        description="允许的文件扩展名",
    )
    upload_dir: Path = Field(default=Path("./uploads"), description="上传目录")

    # ========== Qdrant配置 ==========
    qdrant_host: str = Field(default="localhost", description="Qdrant主机地址")
    qdrant_port: int = Field(default=6333, gt=0, lt=65536, description="Qdrant端口")
    qdrant_collection: str = Field(default="documents", description="Qdrant集合名称")
    qdrant_user: str = Field(default="", description="Qdrant用户名")
    qdrant_password: str = Field(default="", description="Qdrant密码")

    # ========== 嵌入模型配置 ==========
    embedding_model: str = Field(default="text-embedding-v4", description="嵌入模型")
    embedding_batch_size: int = Field(default=100, gt=0, description="嵌入批处理大小")

    # ========== 文档处理配置 ==========
    chunk_size: int = Field(default=1000, gt=0, le=8000, description="文档分块大小")
    chunk_overlap: int = Field(default=200, ge=0, description="文档分块重叠")
    tokenizer_name: str = Field(default="tiktoken", description="Tokenizer类型")
    encoding_name: str = Field(default="cl100k_base", description="编码器名称")
    top_k: int = Field(default=5, gt=0, le=100, description="搜索返回数量")

    # ========== 日志配置 ==========
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式 (json/text)")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")

    # ========== OpenTelemetry配置 ==========
    otel_enabled: bool = Field(default=False, description="启用OpenTelemetry")
    otel_service_name: str = Field(default="document-api", description="服务名称")
    otel_exporter_endpoint: Optional[str] = Field(
        default=None, description="导出器端点"
    )

    # ========== Prometheus配置 ==========
    prometheus_enabled: bool = Field(default=True, description="启用Prometheus指标")
    prometheus_path: str = Field(default="/metrics", description="Prometheus指标路径")

    # ========== Redis配置(可选 - 用于缓存) ==========
    redis_enabled: bool = Field(default=False, description="启用Redis缓存")
    redis_host: str = Field(default="localhost", description="Redis主机地址")
    redis_port: int = Field(default=6379, gt=0, lt=65536, description="Redis端口")
    redis_db: int = Field(default=0, ge=0, description="Redis数据库")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")
    cache_ttl: int = Field(default=300, gt=0, description="缓存TTL(秒)")

    # ========== 数据库配置 ==========
    database_url: str = Field(
        default="sqlite:///./data/app.db",
        description="数据库连接URL（支持SQLite/PostgreSQL/MySQL）",
    )
    db_pool_size: int = Field(default=5, gt=0, le=20, description="数据库连接池大小")
    db_max_overflow: int = Field(
        default=10, gt=0, le=50, description="数据库连接池最大溢出"
    )
    db_echo: bool = Field(default=False, description="是否输出SQL日志")

    @field_validator("upload_dir")
    @classmethod
    def create_upload_dir(cls, v: Path) -> Path:
        """确保上传目录存在"""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """验证chunk_overlap小于chunk_size"""
        chunk_size = info.data.get("chunk_size", 1000)
        if v >= chunk_size:
            raise ValueError(f"chunk_overlap ({v}) 必须小于 chunk_size ({chunk_size})")
        return v

    @property
    def docs_url(self) -> str:
        """获取API文档URL"""
        return f"{self.api_v1_prefix}/docs" if self.debug else ""

    @property
    def redoc_url(self) -> str:
        """获取ReDoc文档URL"""
        return f"{self.api_v1_prefix}/redoc" if self.debug else ""

    @property
    def openapi_url(self) -> str:
        """获取OpenAPI JSON URL"""
        return f"{self.api_v1_prefix}/openapi.json" if self.debug else ""


# 创建全局设置实例
settings = Settings()


# 配置日志
def setup_logging():
    """配置日志系统"""
    import logging
    import sys
    from pathlib import Path

    # 设置日志级别
    log_level = getattr(logging, settings.log_level, logging.INFO)

    # 基础配置
    handlers = [logging.StreamHandler(sys.stdout)]

    # 文件日志
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))

    # JSON格式日志
    if settings.log_format == "json":
        if json_log_formatter:
            formatter = json_log_formatter.JSONFormatter()
            for handler in handlers:
                handler.setFormatter(formatter)
        else:
            # 如果没有json_log_formatter，使用标准格式
            pass

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info(
        f"日志系统已初始化 - 级别: {settings.log_level}, 格式: {settings.log_format}"
    )


if __name__ == "__main__":
    # 测试配置
    print(f"应用名称: {settings.app_name}")
    print(f"API版本: {settings.app_version}")
    print(f"调试模式: {settings.debug}")
    print(f"Qdrant地址: {settings.qdrant_host}:{settings.qdrant_port}")
    print(f"上传目录: {settings.upload_dir}")
    print(f"最大上传大小: {settings.max_upload_size / 1024 / 1024}MB")
