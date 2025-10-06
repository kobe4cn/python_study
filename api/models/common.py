"""
通用API模型
包括分页、查询参数、响应模型等
"""

from __future__ import annotations

from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


# ==================== 排序和过滤 ====================


class SortOrder(str, Enum):
    """排序方向"""

    ASC = "asc"
    DESC = "desc"


class QueryParams(BaseModel):
    """统一查询参数

    Example:
        >>> params = QueryParams(
        ...     page=1,
        ...     page_size=20,
        ...     sort_by="created_at",
        ...     order="desc",
        ...     search="keyword"
        ... )
    """

    # 分页参数
    page: int = Field(default=1, ge=1, description="页码,从1开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量,最大100")

    # 排序参数
    sort_by: Optional[str] = Field(default="created_at", description="排序字段")
    order: SortOrder = Field(default=SortOrder.DESC, description="排序方向")

    # 搜索参数
    search: Optional[str] = Field(default=None, description="搜索关键词")

    # 过滤参数 (JSON格式)
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")

    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """获取限制数量"""
        return self.page_size

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset,
            "limit": self.limit,
            "sort_by": self.sort_by,
            "order": self.order.value,
            "search": self.search,
            "filters": self.filters,
        }


# ==================== 分页响应 ====================

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """分页元数据"""

    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total: int = Field(..., description="总记录数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型

    Generic类型,支持任意数据类型的分页响应

    Example:
        >>> from api.models.user import User
        >>> response = PaginatedResponse[User](
        ...     items=[user1, user2],
        ...     meta=PaginationMeta(
        ...         page=1,
        ...         page_size=20,
        ...         total=100,
        ...         total_pages=5,
        ...         has_next=True,
        ...         has_prev=False
        ...     )
        ... )
    """

    items: List[T] = Field(..., description="数据列表")
    meta: PaginationMeta = Field(..., description="分页元数据")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """创建分页响应

        Args:
            items: 数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页数量

        Returns:
            分页响应对象

        Example:
            >>> response = PaginatedResponse.create(
            ...     items=[user1, user2],
            ...     total=100,
            ...     page=1,
            ...     page_size=20
            ... )
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

        return cls(items=items, meta=meta)


# ==================== API响应包装 ====================


class APIResponse(BaseModel, Generic[T]):
    """标准API响应

    包装所有API响应,提供统一的结构

    Example:
        >>> response = APIResponse.success(
        ...     data={"user_id": 123},
        ...     message="用户创建成功"
        ... )
        >>>
        >>> error_response = APIResponse.error(
        ...     message="用户不存在",
        ...     error_code="USER_NOT_FOUND"
        ... )
    """

    success: bool = Field(..., description="请求是否成功")
    message: str = Field(default="", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    error_type: Optional[str] = Field(default=None, description="错误类型")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    @classmethod
    def success(
        cls,
        data: Optional[T] = None,
        message: str = "Success",
    ) -> "APIResponse[T]":
        """创建成功响应

        Args:
            data: 响应数据
            message: 成功消息

        Returns:
            成功响应对象
        """
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(
        cls,
        message: str,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
    ) -> "APIResponse[None]":
        """创建错误响应

        Args:
            message: 错误消息
            error_code: 错误代码
            error_type: 错误类型

        Returns:
            错误响应对象
        """
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            error_type=error_type,
        )


# ==================== 批量操作 ====================


class BulkOperationRequest(BaseModel):
    """批量操作请求

    Example:
        >>> request = BulkOperationRequest(
        ...     ids=["id1", "id2", "id3"],
        ...     operation="delete"
        ... )
    """

    ids: List[str] = Field(..., min_length=1, max_length=100, description="ID列表")
    operation: Optional[str] = Field(default=None, description="操作类型")
    params: Dict[str, Any] = Field(default_factory=dict, description="额外参数")

    @field_validator("ids")
    @classmethod
    def validate_ids(cls, v: List[str]) -> List[str]:
        """验证ID列表"""
        if len(v) > 100:
            raise ValueError("批量操作最多支持100个ID")
        return v


class BulkOperationResponse(BaseModel):
    """批量操作响应

    Example:
        >>> response = BulkOperationResponse(
        ...     success_count=10,
        ...     failed_count=2,
        ...     total=12,
        ...     errors=[{"id": "id1", "error": "Not found"}]
        ... )
    """

    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    total: int = Field(..., description="总数量")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    details: Optional[Dict[str, Any]] = Field(default=None, description="详细信息")


# ==================== API版本 ====================


class APIVersion(BaseModel):
    """API版本信息"""

    version: str = Field(..., description="版本号")
    deprecated: bool = Field(default=False, description="是否已弃用")
    sunset_date: Optional[datetime] = Field(default=None, description="停用日期")
    migration_guide: Optional[str] = Field(default=None, description="迁移指南URL")


class APIVersionInfo(BaseModel):
    """完整API版本信息"""

    current: str = Field(..., description="当前版本")
    supported: List[str] = Field(..., description="支持的版本列表")
    deprecated: List[str] = Field(default_factory=list, description="已弃用的版本")
    latest: str = Field(..., description="最新版本")
