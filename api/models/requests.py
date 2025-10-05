"""
API请求模型
定义所有API端点的请求数据结构
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator
from pathlib import Path


class DocumentUploadRequest(BaseModel):
    """文件上传请求（通过multipart/form-data处理，这里用于文档）"""

    collection_name: str = Field(
        default="documents",
        min_length=1,
        max_length=100,
        description="目标集合名称"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="文档元数据"
    )
    chunk_size: Optional[int] = Field(
        default=None,
        gt=0,
        le=8000,
        description="分块大小（覆盖默认配置）"
    )
    chunk_overlap: Optional[int] = Field(
        default=None,
        ge=0,
        description="分块重叠（覆盖默认配置）"
    )

    @field_validator("collection_name")
    @classmethod
    def validate_collection_name(cls, v: str) -> str:
        """验证集合名称格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("集合名称只能包含字母、数字、下划线和连字符")
        return v


class URLLoadRequest(BaseModel):
    """从URL加载文档请求"""

    urls: List[HttpUrl] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="要加载的URL列表"
    )
    collection_name: str = Field(
        default="documents",
        min_length=1,
        max_length=100,
        description="目标集合名称"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="文档元数据"
    )
    chunk_size: Optional[int] = Field(
        default=None,
        gt=0,
        le=8000,
        description="分块大小"
    )
    chunk_overlap: Optional[int] = Field(
        default=None,
        ge=0,
        description="分块重叠"
    )

    @field_validator("collection_name")
    @classmethod
    def validate_collection_name(cls, v: str) -> str:
        """验证集合名称格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("集合名称只能包含字母、数字、下划线和连字符")
        return v

    @model_validator(mode='after')
    def validate_chunk_overlap(self) -> URLLoadRequest:
        """验证chunk_overlap小于chunk_size"""
        if self.chunk_size and self.chunk_overlap:
            if self.chunk_overlap >= self.chunk_size:
                raise ValueError("chunk_overlap必须小于chunk_size")
        return self


class SearchRequest(BaseModel):
    """搜索请求"""

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="搜索查询文本"
    )
    collection_name: str = Field(
        default="documents",
        min_length=1,
        description="集合名称"
    )
    top_k: int = Field(
        default=5,
        gt=0,
        le=100,
        description="返回结果数量"
    )
    filter_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="元数据过滤条件"
    )
    include_metadata: bool = Field(
        default=True,
        description="是否包含元数据"
    )
    include_scores: bool = Field(
        default=True,
        description="是否包含相似度分数"
    )


class BatchSearchRequest(BaseModel):
    """批量搜索请求"""

    queries: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="搜索查询列表"
    )
    collection_name: str = Field(
        default="documents",
        min_length=1,
        description="集合名称"
    )
    top_k: int = Field(
        default=5,
        gt=0,
        le=100,
        description="每个查询返回的结果数量"
    )
    filter_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="元数据过滤条件"
    )

    @field_validator("queries")
    @classmethod
    def validate_queries(cls, v: List[str]) -> List[str]:
        """验证查询列表"""
        for query in v:
            if not query.strip():
                raise ValueError("查询文本不能为空")
            if len(query) > 1000:
                raise ValueError("单个查询文本长度不能超过1000字符")
        return v


class CollectionCreateRequest(BaseModel):
    """创建集合请求"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="集合名称"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="集合描述"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="集合元数据"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证集合名称格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("集合名称只能包含字母、数字、下划线和连字符")
        return v


class UpdateDocumentRequest(BaseModel):
    """更新文档请求"""

    metadata: Dict[str, Any] = Field(
        ...,
        description="要更新的元数据"
    )


class DeleteDocumentRequest(BaseModel):
    """删除文档请求"""

    doc_ids: Optional[List[str]] = Field(
        default=None,
        description="要删除的文档ID列表"
    )
    filter_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="根据元数据过滤删除"
    )

    @model_validator(mode='after')
    def validate_at_least_one(self) -> DeleteDocumentRequest:
        """至少需要提供一种删除方式"""
        if not self.doc_ids and not self.filter_metadata:
            raise ValueError("必须提供doc_ids或filter_metadata中的至少一个")
        return self


class HealthCheckRequest(BaseModel):
    """健康检查请求（可选参数）"""

    check_dependencies: bool = Field(
        default=True,
        description="是否检查依赖服务（Qdrant等）"
    )


class SplitTextRequest(BaseModel):
    """文本分割请求"""

    text: str = Field(
        ...,
        min_length=1,
        description="要分割的文本"
    )
    chunk_size: int = Field(
        default=1000,
        gt=0,
        le=8000,
        description="分块大小"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        description="分块重叠"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="文本元数据"
    )

    @model_validator(mode='after')
    def validate_chunk_overlap(self) -> SplitTextRequest:
        """验证chunk_overlap小于chunk_size"""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap必须小于chunk_size")
        return self


class TokenRequest(BaseModel):
    """JWT令牌请求"""

    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="用户名"
    )
    password: str = Field(
        ...,
        min_length=1,
        description="密码"
    )


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""

    refresh_token: str = Field(
        ...,
        min_length=1,
        description="刷新令牌"
    )


# 导出所有请求模型
__all__ = [
    "DocumentUploadRequest",
    "URLLoadRequest",
    "SearchRequest",
    "BatchSearchRequest",
    "CollectionCreateRequest",
    "UpdateDocumentRequest",
    "DeleteDocumentRequest",
    "HealthCheckRequest",
    "SplitTextRequest",
    "TokenRequest",
    "RefreshTokenRequest",
]
