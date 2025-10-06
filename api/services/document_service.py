"""
文档管理服务
处理文档上传、加载、分割、存储等业务逻辑
"""

from __future__ import annotations

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from langchain_core.documents import Document

from api.config import settings
from api.dependencies import (
    get_vector_store,
    get_document_loader,
    get_document_splitter
)
from doc.loader.doc_loader import LoadError

logger = logging.getLogger(__name__)


class DocumentService:
    """文档管理服务类"""

    def __init__(self):
        """初始化文档服务"""
        self.upload_dir = settings.upload_dir
        self._file_lock = asyncio.Lock()  # 实例级文件锁,保护并发文件操作

    async def process_file_upload(
        self,
        file_content: bytes,
        filename: str,
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> Tuple[List[str], int, List[str]]:
        """
        处理文件上传

        Args:
            file_content: 文件内容
            filename: 文件名
            collection_name: 集合名称
            metadata: 元数据
            chunk_size: 分块大小
            chunk_overlap: 分块重叠

        Returns:
            (文档ID列表, 总分块数, 错误列表)
        """
        logger.info(f"处理文件上传: {filename}, 大小: {len(file_content)} bytes")

        try:
            # 1. 保存文件
            file_path = await self._save_uploaded_file(file_content, filename)

            # 2. 加载文档
            loader = get_document_loader(doc_type="file", doc_paths=[str(file_path)])
            docs, errors = await asyncio.to_thread(loader.load)

            if not docs:
                error_msgs = [str(e) for e in errors]
                logger.error(f"文件加载失败: {filename}")
                return [], 0, error_msgs

            # 3. 添加自定义元数据
            if metadata:
                for doc in docs:
                    doc.metadata.update(metadata)

            # 4. 分割文档
            splitter = get_document_splitter(chunk_size, chunk_overlap)
            split_docs = await asyncio.to_thread(splitter.split, docs)

            logger.info(f"文档分割完成: {len(split_docs)} 个块")

            # 5. 存储到向量数据库
            vstore = get_vector_store(collection_name)
            doc_ids = await asyncio.to_thread(vstore.add_documents, split_docs)

            logger.info(f"文档存储完成: {len(doc_ids)} 个ID")

            error_msgs = [str(e) for e in errors]
            return doc_ids, len(split_docs), error_msgs

        except Exception as e:
            logger.exception(f"文件上传处理失败: {e}")
            return [], 0, [str(e)]

    async def process_url_loading(
        self,
        urls: List[str],
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> Tuple[List[str], int, int, int, List[Dict[str, str]]]:
        """
        处理URL加载

        Args:
            urls: URL列表
            collection_name: 集合名称
            metadata: 元数据
            chunk_size: 分块大小
            chunk_overlap: 分块重叠

        Returns:
            (文档ID列表, 总分块数, 成功数, 失败数, 错误详情)
        """
        logger.info(f"处理URL加载: {len(urls)} 个URL")

        try:
            # 1. 加载URL
            url_strings = [str(url) for url in urls]
            loader = get_document_loader(doc_type="url", doc_paths=url_strings)
            docs, errors = await asyncio.to_thread(loader.load)

            # 2. 添加自定义元数据
            if metadata:
                for doc in docs:
                    doc.metadata.update(metadata)

            # 3. 分割文档
            if docs:
                splitter = get_document_splitter(chunk_size, chunk_overlap)
                split_docs = await asyncio.to_thread(splitter.split, docs)

                logger.info(f"URL文档分割完成: {len(split_docs)} 个块")

                # 4. 存储到向量数据库
                vstore = get_vector_store(collection_name)
                doc_ids = await asyncio.to_thread(vstore.add_documents, split_docs)

                logger.info(f"URL文档存储完成: {len(doc_ids)} 个ID")
            else:
                split_docs = []
                doc_ids = []

            # 5. 构建错误详情
            error_details = [
                {
                    "url": err.file_path,
                    "error": str(err.error),
                    "error_type": err.error_type
                }
                for err in errors
            ]

            urls_loaded = len(urls) - len(errors)
            urls_failed = len(errors)

            return doc_ids, len(split_docs), urls_loaded, urls_failed, error_details

        except Exception as e:
            logger.exception(f"URL加载处理失败: {e}")
            return [], 0, 0, len(urls), [{"error": str(e)}]

    async def delete_documents(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any]
    ) -> bool:
        """
        删除文档

        Args:
            collection_name: 集合名称
            metadata_filter: 元数据过滤条件

        Returns:
            是否成功
        """
        try:
            vstore = get_vector_store(collection_name)
            await asyncio.to_thread(
                vstore.vstore.delete_documents_by_metadata,
                metadata_filter
            )
            logger.info(f"文档删除成功: {metadata_filter}")
            return True
        except Exception as e:
            logger.error(f"文档删除失败: {e}")
            return False

    async def get_collection_info(
        self,
        collection_name: str
    ) -> Dict[str, Any]:
        """
        获取集合信息

        Args:
            collection_name: 集合名称

        Returns:
            集合信息字典
        """
        try:
            vstore = get_vector_store(collection_name)
            info = await asyncio.to_thread(vstore.vstore.get_collection_info)
            return info
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            raise

    async def split_text(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        分割文本

        Args:
            text: 待分割的文本
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            metadata: 元数据

        Returns:
            分割后的文本块列表
        """
        try:
            splitter = get_document_splitter(chunk_size, chunk_overlap)
            chunks = await asyncio.to_thread(
                splitter.split_text,
                text,
                metadata
            )

            return [
                {
                    "content": chunk.page_content,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ]
        except Exception as e:
            logger.error(f"文本分割失败: {e}")
            raise

    async def _save_uploaded_file(
        self,
        file_content: bytes,
        filename: str
    ) -> Path:
        """
        保存上传的文件

        Args:
            file_content: 文件内容
            filename: 文件名

        Returns:
            文件路径
        """
        # 确保上传目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # 生成安全的文件名
        safe_filename = self._sanitize_filename(filename)
        file_path = self.upload_dir / safe_filename

        # 如果文件已存在，添加时间戳
        if file_path.exists():
            import time
            timestamp = int(time.time())
            name = file_path.stem
            suffix = file_path.suffix
            file_path = self.upload_dir / f"{name}_{timestamp}{suffix}"

        # 异步写入文件 - 使用实例级锁保护并发访问
        async with self._file_lock:
            # 使用线程池执行IO操作,避免阻塞事件循环
            await asyncio.to_thread(self._write_file_sync, file_path, file_content)

        logger.info(f"文件已保存: {file_path}")
        return file_path

    @staticmethod
    def _write_file_sync(file_path: Path, content: bytes) -> None:
        """
        同步写入文件(在线程池中执行)

        Args:
            file_path: 文件路径
            content: 文件内容
        """
        with open(file_path, "wb") as f:
            f.write(content)

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        清理文件名，防止路径遍历攻击

        Args:
            filename: 原始文件名

        Returns:
            安全的文件名
        """
        import re

        # 移除路径分隔符
        filename = filename.replace("/", "_").replace("\\", "_")

        # 移除危险字符
        filename = re.sub(r'[^\w\s.-]', '', filename)

        # 限制长度
        if len(filename) > 255:
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
            filename = name[:250] + ("." + ext if ext else "")

        return filename

    @staticmethod
    def validate_file_type(filename: str, content_type: str) -> bool:
        """
        验证文件类型

        Args:
            filename: 文件名
            content_type: Content-Type

        Returns:
            是否为允许的文件类型
        """
        # 检查扩展名
        file_ext = Path(filename).suffix.lower()
        if file_ext not in settings.allowed_file_extensions:
            logger.warning(f"不允许的文件扩展名: {file_ext}")
            return False

        # 检查MIME类型
        if content_type not in settings.allowed_file_types:
            logger.warning(f"不允许的文件类型: {content_type}")
            return False

        return True


# 导出
__all__ = ["DocumentService"]
