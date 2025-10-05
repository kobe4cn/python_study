"""
文档管理路由
处理文档上传、加载、删除等操作
"""

from __future__ import annotations

import logging
from typing import Optional
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    Depends,
    Request
)
from fastapi.responses import JSONResponse

from api.models.requests import URLLoadRequest, DeleteDocumentRequest
from api.models.responses import (
    DocumentUploadResponse,
    URLLoadResponse,
    MessageResponse,
    ErrorResponse
)
from api.services.document_service import DocumentService
from api.security.auth import get_current_user, require_permission
from api.config import settings
from api.middleware.rate_limit import limiter, get_upload_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["文档管理"]
)

# 文档服务实例
doc_service = DocumentService()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="上传文档文件",
    description="上传文档文件并自动处理、分割、存储到向量数据库"
)
@limiter.limit(get_upload_rate_limit())
async def upload_document(
    request: Request,
    file: UploadFile = File(..., description="文档文件"),
    collection_name: str = Form(default="documents", description="目标集合名称"),
    chunk_size: Optional[int] = Form(default=None, description="分块大小"),
    chunk_overlap: Optional[int] = Form(default=None, description="分块重叠"),
    current_user: dict = Depends(require_permission("document:create"))
):
    """
    上传文档文件 - 需要 document:create 权限

    - **file**: 文档文件（支持PDF、TXT、MD、DOCX等格式）
    - **collection_name**: 目标向量存储集合
    - **chunk_size**: 自定义分块大小（可选）
    - **chunk_overlap**: 自定义分块重叠（可选）

    返回上传后的文档ID列表和分块信息
    """
    logger.info(
        f"用户操作: {current_user['username']} 上传文档 - {file.filename}"
    )

    try:
        # 1. 验证文件大小
        file_size = 0
        content = await file.read()
        file_size = len(content)

        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件过大，最大允许 {settings.max_upload_size / 1024 / 1024}MB"
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件为空"
            )

        # 2. 验证文件类型
        if not DocumentService.validate_file_type(
            file.filename or "unknown",
            file.content_type or "application/octet-stream"
        ):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"不支持的文件类型: {file.content_type}"
            )

        # 3. 处理文件
        doc_ids, total_chunks, errors = await doc_service.process_file_upload(
            file_content=content,
            filename=file.filename or "unknown",
            collection_name=collection_name,
            metadata={
                "original_filename": file.filename,
                "content_type": file.content_type,
                "file_size": file_size,
                "created_by": current_user["username"],
                "user_role": current_user.get("role", "user")
            },
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        if not doc_ids and errors:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件处理失败: {'; '.join(errors)}"
            )

        return DocumentUploadResponse(
            success=True,
            message="文件上传成功",
            doc_ids=doc_ids,
            total_chunks=total_chunks,
            collection_name=collection_name,
            file_name=file.filename,
            file_size=file_size,
            errors=errors
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"文件上传失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/from-url",
    response_model=URLLoadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="从URL加载文档",
    description="从URL加载网页内容并处理、分割、存储"
)
@limiter.limit(get_upload_rate_limit())
async def load_from_url(
    request: Request,
    url_request: URLLoadRequest,
    current_user: dict = Depends(require_permission("document:create"))
):
    """
    从URL加载文档 - 需要 document:create 权限

    - **urls**: URL列表（最多10个）
    - **collection_name**: 目标集合名称
    - **metadata**: 自定义元数据（可选）
    - **chunk_size**: 分块大小（可选）
    - **chunk_overlap**: 分块重叠（可选）
    """
    logger.info(
        f"用户操作: {current_user['username']} 从URL加载文档 - {len(url_request.urls)} 个URL"
    )

    try:
        # 添加创建者信息到元数据
        enhanced_metadata = url_request.metadata or {}
        enhanced_metadata.update({
            "created_by": current_user["username"],
            "user_role": current_user.get("role", "user")
        })

        doc_ids, total_chunks, loaded, failed, errors = await doc_service.process_url_loading(
            urls=url_request.urls,
            collection_name=url_request.collection_name,
            metadata=enhanced_metadata,
            chunk_size=url_request.chunk_size,
            chunk_overlap=url_request.chunk_overlap
        )

        return URLLoadResponse(
            success=True,
            message=f"成功加载 {loaded} 个URL",
            doc_ids=doc_ids,
            total_chunks=total_chunks,
            collection_name=url_request.collection_name,
            urls_loaded=loaded,
            urls_failed=failed,
            errors=errors
        )

    except Exception as e:
        logger.exception(f"URL加载失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{collection_name}",
    response_model=MessageResponse,
    summary="删除文档",
    description="根据元数据过滤条件删除文档"
)
async def delete_documents(
    collection_name: str,
    delete_request: DeleteDocumentRequest,
    current_user: dict = Depends(require_permission("document:delete"))
):
    """
    删除文档 - 需要 document:delete 权限

    - **collection_name**: 集合名称
    - **filter_metadata**: 元数据过滤条件

    普通用户只能删除自己创建的文档，管理员可以删除所有文档
    """
    logger.info(
        f"用户操作: {current_user['username']} 删除文档 - collection={collection_name}"
    )

    try:
        if delete_request.filter_metadata:
            # 如果不是管理员，只能删除自己创建的文档
            metadata_filter = delete_request.filter_metadata.copy()
            if current_user.get("role") != "admin":
                metadata_filter["created_by"] = current_user["username"]
                logger.info(
                    f"非管理员用户 {current_user['username']} 添加过滤条件: created_by"
                )

            success = await doc_service.delete_documents(
                collection_name=collection_name,
                metadata_filter=metadata_filter
            )

            if success:
                # 审计日志
                logger.info(
                    f"审计日志: 用户 {current_user['username']} "
                    f"删除文档成功 - collection={collection_name}, "
                    f"filter={metadata_filter}"
                )
                return MessageResponse(
                    success=True,
                    message="文档删除成功"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="文档删除失败"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供filter_metadata"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"文档删除失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# 导出
__all__ = ["router"]
