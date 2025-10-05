"""
API响应模型
定义所有API端点的响应数据结构
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """基础响应模型"""

    success: bool = Field(default=True, description="请求是否成功")
    message: Optional[str] = Field(default=None, description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")


class ErrorResponse(BaseResponse):
    """错误响应"""

    success: bool = Field(default=False, description="请求失败")
    error_code: str = Field(..., description="错误代码")
    error_type: str = Field(..., description="错误类型")
    detail: Optional[str] = Field(default=None, description="错误详情")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="详细错误列表")


class MessageResponse(BaseResponse):
    """简单消息响应"""

    data: Optional[Dict[str, Any]] = Field(default=None, description="额外数据")


class DocumentResponse(BaseResponse):
    """文档响应"""

    doc_id: str = Field(..., description="文档ID")
    content: Optional[str] = Field(default=None, description="文档内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文档元数据")
    collection_name: str = Field(..., description="所属集合")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")


class DocumentListResponse(BaseResponse):
    """文档列表响应"""

    documents: List[DocumentResponse] = Field(default_factory=list, description="文档列表")
    total: int = Field(..., description="文档总数")
    page: Optional[int] = Field(default=None, description="当前页码")
    page_size: Optional[int] = Field(default=None, description="每页数量")


class DocumentUploadResponse(BaseResponse):
    """文档上传响应"""

    doc_ids: List[str] = Field(..., description="上传后的文档ID列表")
    total_chunks: int = Field(..., description="总分块数")
    collection_name: str = Field(..., description="集合名称")
    file_name: Optional[str] = Field(default=None, description="文件名")
    file_size: Optional[int] = Field(default=None, description="文件大小（字节）")
    errors: List[str] = Field(default_factory=list, description="处理错误列表")


class URLLoadResponse(BaseResponse):
    """URL加载响应"""

    doc_ids: List[str] = Field(..., description="加载后的文档ID列表")
    total_chunks: int = Field(..., description="总分块数")
    collection_name: str = Field(..., description="集合名称")
    urls_loaded: int = Field(..., description="成功加载的URL数量")
    urls_failed: int = Field(default=0, description="加载失败的URL数量")
    errors: List[Dict[str, str]] = Field(default_factory=list, description="错误详情")


class SearchResultItem(BaseModel):
    """搜索结果项"""

    doc_id: str = Field(..., description="文档ID")
    content: str = Field(..., description="文档内容")
    score: Optional[float] = Field(default=None, description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文档元数据")
    highlights: Optional[List[str]] = Field(default=None, description="高亮片段")


class SearchResponse(BaseResponse):
    """搜索响应"""

    query: str = Field(..., description="搜索查询")
    results: List[SearchResultItem] = Field(default_factory=list, description="搜索结果")
    total: int = Field(..., description="结果总数")
    took_ms: Optional[float] = Field(default=None, description="搜索耗时（毫秒）")
    collection_name: str = Field(..., description="搜索的集合")


class BatchSearchResponse(BaseResponse):
    """批量搜索响应"""

    results: List[SearchResponse] = Field(..., description="搜索结果列表")
    total_queries: int = Field(..., description="查询总数")
    took_ms: Optional[float] = Field(default=None, description="总耗时（毫秒）")


class CollectionResponse(BaseResponse):
    """集合响应"""

    name: str = Field(..., description="集合名称")
    description: Optional[str] = Field(default=None, description="集合描述")
    vectors_count: int = Field(default=0, description="向量数量")
    points_count: int = Field(default=0, description="点数量")
    status: str = Field(default="unknown", description="集合状态")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="集合元数据")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")


class CollectionListResponse(BaseResponse):
    """集合列表响应"""

    collections: List[CollectionResponse] = Field(default_factory=list, description="集合列表")
    total: int = Field(..., description="集合总数")


class CollectionInfoResponse(BaseResponse):
    """集合详细信息响应"""

    collection: CollectionResponse = Field(..., description="集合信息")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="统计信息")


class HealthResponse(BaseResponse):
    """健康检查响应"""

    status: str = Field(..., description="服务状态 (healthy/unhealthy)")
    version: str = Field(..., description="API版本")
    uptime_seconds: float = Field(..., description="运行时间（秒）")
    dependencies: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="依赖服务状态"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status": "healthy",
                "version": "1.0.0",
                "uptime_seconds": 3600.5,
                "timestamp": "2025-10-04T12:00:00Z",
                "dependencies": {
                    "qdrant": {
                        "status": "healthy",
                        "latency_ms": 5.2
                    },
                    "redis": {
                        "status": "healthy",
                        "latency_ms": 1.1
                    }
                }
            }
        }


class TokenResponse(BaseResponse):
    """JWT令牌响应"""

    access_token: str = Field(..., description="访问令牌")
    refresh_token: Optional[str] = Field(default=None, description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class StatisticsResponse(BaseResponse):
    """统计信息响应"""

    total_documents: int = Field(..., description="文档总数")
    total_collections: int = Field(..., description="集合总数")
    total_vectors: int = Field(..., description="向量总数")
    storage_size_bytes: Optional[int] = Field(default=None, description="存储大小（字节）")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="详细统计")


class DocumentSplitResponse(BaseResponse):
    """文档分割响应"""

    chunks: List[Dict[str, Any]] = Field(..., description="分割后的文本块")
    total_chunks: int = Field(..., description="总块数")
    chunk_size: int = Field(..., description="使用的块大小")
    chunk_overlap: int = Field(..., description="使用的重叠大小")


# 导出所有响应模型
__all__ = [
    "BaseResponse",
    "ErrorResponse",
    "MessageResponse",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentUploadResponse",
    "URLLoadResponse",
    "SearchResultItem",
    "SearchResponse",
    "BatchSearchResponse",
    "CollectionResponse",
    "CollectionListResponse",
    "CollectionInfoResponse",
    "HealthResponse",
    "TokenResponse",
    "StatisticsResponse",
    "DocumentSplitResponse",
]
