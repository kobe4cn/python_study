"""
分页工具函数
提供通用的分页查询和响应构建功能
"""

from __future__ import annotations

from typing import List, TypeVar, Generic, Callable, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.models.common import PaginatedResponse, QueryParams

T = TypeVar("T")


def paginate_query(
    session: Session,
    query: Any,
    params: QueryParams,
    model_class: type,
) -> PaginatedResponse[T]:
    """
    对SQLAlchemy查询进行分页

    Args:
        session: 数据库会话
        query: SQLAlchemy查询对象
        params: 查询参数
        model_class: 模型类

    Returns:
        分页响应对象

    Example:
        >>> from api.database.models import User
        >>> query = select(User).where(User.is_active == True)
        >>> result = paginate_query(session, query, params, User)
    """
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0

    # 应用排序
    if params.sort_by:
        order_column = getattr(model_class, params.sort_by, None)
        if order_column is not None:
            if params.order.value == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())

    # 应用分页
    query = query.offset(params.offset).limit(params.limit)

    # 执行查询
    items = session.execute(query).scalars().all()

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


def paginate_list(
    items: List[T],
    params: QueryParams,
) -> PaginatedResponse[T]:
    """
    对Python列表进行分页

    Args:
        items: 数据列表
        params: 查询参数

    Returns:
        分页响应对象

    Example:
        >>> items = [1, 2, 3, 4, 5]
        >>> params = QueryParams(page=1, page_size=2)
        >>> result = paginate_list(items, params)
        >>> print(result.items)  # [1, 2]
    """
    total = len(items)
    start = params.offset
    end = start + params.limit

    paginated_items = items[start:end]

    return PaginatedResponse.create(
        items=paginated_items,
        total=total,
        page=params.page,
        page_size=params.page_size,
    )
