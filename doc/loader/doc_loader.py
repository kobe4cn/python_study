"""
文档加载器
支持URL和文件加载
"""

from __future__ import annotations

from typing import List, Tuple, Literal
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from markitdown import MarkItDown
import html2text
import logging
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class LoadError:
    """加载错误信息"""

    file_path: str
    error: Exception
    error_type: str

    def __str__(self) -> str:
        return f"加载失败 [{self.error_type}]: {self.file_path} - {str(self.error)}"


class DocLoaderConfig(BaseModel):
    """文档加载器配置"""

    doc_type: Literal["url", "file"] = Field(..., description="文档类型")
    doc_paths: List[str] = Field(..., min_length=1, description="文档路径列表")

    @field_validator("doc_paths")
    @classmethod
    def validate_paths(cls, v: List[str], info) -> List[str]:
        """验证路径有效性"""
        if info.data.get("doc_type") == "file":
            for path in v:
                if not Path(path).exists():
                    logger.warning(f"文件路径不存在: {path}")
        return v

    @field_validator("doc_paths")
    @classmethod
    def validate_urls(cls, v: List[str], info) -> List[str]:
        """验证URL有效性"""
        if info.data.get("doc_type") == "url":
            for url in v:
                if not url.startswith(("http://", "https://")):
                    raise ValueError(f"无效的URL格式: {url}")
        return v


class DocLoader:
    """文档加载器，支持URL和文件加载"""

    def __init__(self, doc_type: Literal["url", "file"], doc_path: List[str]) -> None:
        """初始化文档加载器

        Args:
            doc_type: 文档类型，"url"或"file"
            doc_path: 文档路径列表

        Raises:
            ValueError: 当配置验证失败时
        """
        self.config = DocLoaderConfig(doc_type=doc_type, doc_paths=doc_path)
        self._html_converter = html2text.HTML2Text()
        self._html_converter.ignore_links = False
        self._html_converter.ignore_images = False

    def load(self) -> Tuple[List[Document], List[LoadError]]:
        """加载文档

        Returns:
            文档列表和错误列表的元组
        """
        match self.config.doc_type:
            case "url":
                return self.load_url()
            case "file":
                return self.load_file()
            case _:
                raise ValueError(f"不支持的文档类型: {self.config.doc_type}")

    def load_url(self) -> Tuple[List[Document], List[LoadError]]:
        """加载URL文档

        Returns:
            文档列表和错误列表
        """
        result_docs: List[Document] = []
        errors: List[LoadError] = []

        for url in list(self.config.doc_paths):
            try:
                logger.info(f"正在加载URL: {url}")
                loader = WebBaseLoader(web_path=url)
                docs = loader.load()

                for doc in docs:
                    try:
                        # 转换HTML到Markdown
                        doc.page_content = self._html_converter.handle(doc.page_content)
                        doc.metadata = {"source": url, "type": "url"}
                        result_docs.append(doc)
                    except Exception as e:
                        logger.error(f"HTML转换失败: {url} - {e}")
                        errors.append(
                            LoadError(
                                file_path=doc.metadata.get("source", url),
                                error=e,
                                error_type="html_conversion",
                            )
                        )

                logger.info(f"成功加载URL: {url}, 文档数: {len(docs)}")

            except Exception as e:
                logger.error(f"URL加载失败: {url} - {e}")
                errors.append(
                    LoadError(file_path=url, error=e, error_type="url_loading")
                )

        return result_docs, errors

    def load_file(self) -> Tuple[List[Document], List[LoadError]]:
        """加载文件文档

        Returns:
            文档列表和错误列表
        """
        docs: List[Document] = []
        errors: List[LoadError] = []
        md_converter = MarkItDown()

        for file_path in list(self.config.doc_paths):
            try:
                logger.info(f"正在加载文件: {file_path}")
                path = Path(file_path)

                if not path.exists():
                    raise FileNotFoundError(f"文件不存在: {file_path}")

                if not path.is_file():
                    raise ValueError(f"路径不是文件: {file_path}")

                result = md_converter.convert(str(path))
                docs.append(
                    Document(
                        page_content=result.text_content,
                        metadata={
                            "source": str(path.absolute()),
                            "type": "file",
                            "file_name": path.name,
                            "file_size": path.stat().st_size,
                        },
                    )
                )
                logger.info(f"成功加载文件: {file_path}")

            except (OSError, IOError, ValueError, TypeError) as e:
                logger.error(f"文件加载失败: {file_path} - {e}")
                errors.append(
                    LoadError(file_path=file_path, error=e, error_type=type(e).__name__)
                )

        return docs, errors


if __name__ == "__main__":
    loader = DocLoader(
        "url",
        [
            "https://lilianweng.github.io/posts/2023-06-23-agent/",  # AI代理相关文章
            # "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",  # 提示工程文章
            # "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",  # LLM对抗攻击文章
        ],
    )
    docs, error_urls = loader.load()
    print(len(docs))
    # print(len(error_urls))
    # print(len(docs[0].page_content))
