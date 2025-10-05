"""
FastAPI主应用
生产级文档管理API
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.config import settings, setup_logging
from api.routers import (
    documents_router,
    search_router,
    collections_router,
    health_router,
    auth_router,
    users_router,
    chat_router,
)
from api.middleware.logging import setup_logging_middleware
from api.middleware.rate_limit import setup_rate_limiting
from api.middleware.security import setup_security_middleware
from api.models.responses import ErrorResponse

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    在启动和关闭时执行必要的操作
    """
    # 启动时执行
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 正在启动...")
    logger.info(f"环境: {settings.environment}")
    logger.info(f"调试模式: {settings.debug}")
    logger.info(f"HTTPS: {'已启用' if settings.use_https else '未启用'}")
    logger.info(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
    logger.info(f"速率限制: {'已启用' if settings.rate_limit_enabled else '未启用'}")
    logger.info(f"Redis缓存: {'已启用' if settings.redis_enabled else '未启用'}")
    logger.info("=" * 60)

    # 预热连接（可选）
    try:
        from api.dependencies import check_qdrant_health
        qdrant_status = check_qdrant_health()
        logger.info(f"Qdrant连接状态: {qdrant_status.get('status')}")
    except Exception as e:
        logger.error(f"Qdrant连接检查失败: {e}")

    yield

    # 关闭时执行
    logger.info("🛑 应用正在关闭...")
    logger.info("清理资源...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)


# ========== 设置中间件 ==========

# 1. 日志中间件
setup_logging_middleware(app)

# 2. 安全中间件（CORS、安全头、请求验证等）
setup_security_middleware(app)

# 3. 速率限制
limiter = setup_rate_limiting(app)


# ========== 异常处理器 ==========

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    logger.warning(
        f"HTTP异常: {exc.status_code} - {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message="请求处理失败",
            error_code=f"HTTP_{exc.status_code}",
            error_type="HTTPException",
            detail=str(exc.detail)
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.warning(
        f"请求验证失败: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            message="请求参数验证失败",
            error_code="VALIDATION_ERROR",
            error_type="RequestValidationError",
            detail="请求数据格式不正确",
            errors=exc.errors()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.exception(
        f"未处理的异常: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            message="服务器内部错误",
            error_code="INTERNAL_ERROR",
            error_type=type(exc).__name__,
            detail=str(exc) if settings.debug else "请联系系统管理员"
        ).model_dump()
    )


# ========== 注册路由 ==========

# 健康检查（不需要认证）
app.include_router(health_router)

# 认证路由
app.include_router(auth_router, prefix=settings.api_v1_prefix)

# 业务路由
app.include_router(documents_router, prefix=settings.api_v1_prefix)
app.include_router(search_router, prefix=settings.api_v1_prefix)
app.include_router(collections_router, prefix=settings.api_v1_prefix)
app.include_router(users_router, prefix=settings.api_v1_prefix)
app.include_router(chat_router, prefix=settings.api_v1_prefix)


# ========== 根路由 ==========

@app.get("/", tags=["根路径"])
async def root():
    """API根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs_url": "/docs" if settings.debug else None,
        "health_check": "/health",
        "api_prefix": settings.api_v1_prefix
    }


# ========== Prometheus指标端点（可选） ==========

if settings.prometheus_enabled:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        # 启用Prometheus指标收集
        instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/metrics"],
            env_var_name="ENABLE_METRICS",
            inprogress_name="fastapi_inprogress",
            inprogress_labels=True,
        )

        instrumentator.instrument(app).expose(app, endpoint=settings.prometheus_path)
        logger.info(f"Prometheus指标已启用: {settings.prometheus_path}")

    except ImportError:
        logger.warning("prometheus-fastapi-instrumentator未安装，Prometheus指标未启用")


# ========== OpenTelemetry追踪（可选） ==========

if settings.otel_enabled and settings.otel_exporter_endpoint:
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        # 设置追踪器
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)

        # 配置OTLP导出器
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_endpoint,
            insecure=True
        )

        # 添加批处理span处理器
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )

        # 自动追踪FastAPI
        FastAPIInstrumentor.instrument_app(app)

        logger.info(f"OpenTelemetry追踪已启用: {settings.otel_exporter_endpoint}")

    except ImportError:
        logger.warning("OpenTelemetry依赖未安装，追踪功能未启用")


# ========== 开发服务器启动 ==========

if __name__ == "__main__":
    import uvicorn

    uvicorn_config = {
        "app": "api.main:app",
        "host": settings.host,
        "port": settings.port,
        "reload": settings.reload,
        "workers": 1 if settings.reload else settings.workers,
        "log_level": settings.log_level.lower(),
        "access_log": True,
    }

    # SSL配置
    if settings.use_https:
        from api.security.tls import get_uvicorn_ssl_config
        uvicorn_config.update(get_uvicorn_ssl_config())

    logger.info(f"启动Uvicorn服务器: {settings.host}:{settings.port}")
    uvicorn.run(**uvicorn_config)
