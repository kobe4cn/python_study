from __future__ import annotations
import logging
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_text_splitters import (
    ExperimentalMarkdownSyntaxTextSplitter,
    MarkdownTextSplitter,
    TextSplitter,
)
from tqdm import tqdm
from langchain_core.documents import Document
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


class SplitterConfig(BaseModel):
    """分割器配置"""

    headers: List[tuple[str, str]] = Field(
        default=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5"),
            ("######", "Header 6"),
        ],
        description="Markdown标题配置",
    )
    tokenizer_name: Literal["tiktoken", "huggingface"] = Field(
        ..., description="Tokenizer类型"
    )
    encoding_name: str = Field(..., description="编码器名称")
    chunk_size: int = Field(gt=0, le=8000, description="块大小")
    chunk_overlap: int = Field(ge=0, description="块重叠大小")
    keep_separator: bool = Field(default=True, description="是否保留分隔符")

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v: int, info) -> int:
        """验证重叠大小不超过块大小"""
        chunk_size = info.data.get("chunk_size", 0)
        if v >= chunk_size:
            raise ValueError(f"chunk_overlap ({v}) 必须小于 chunk_size ({chunk_size})")
        return v


class MdSplitter:
    """Markdown文档分割器"""

    def __init__(
        self,
        headers: List[tuple[str, str]],
        tokenizer_name: Literal["tiktoken", "huggingface"],
        encoding_name: str,
        chunk_size: int,
        chunk_overlap: int,
        keep_separator: bool = True,
    ) -> None:
        """初始化分割器

        Args:
            headers: Markdown标题配置
            tokenizer_name: Tokenizer类型
            encoding_name: 编码器名称
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
            keep_separator: 是否保留分隔符
        """
        # 验证配置
        self.config = SplitterConfig(
            headers=headers,
            tokenizer_name=tokenizer_name,
            encoding_name=encoding_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            keep_separator=keep_separator,
        )

        # 初始化标题分割器
        self._header_splitter = ExperimentalMarkdownSyntaxTextSplitter(
            headers_to_split_on=self.config.headers
        )

        # 初始化token分割器
        self._token_splitter = self._initialize_token_splitter()

    def _initialize_token_splitter(self) -> TextSplitter:
        """初始化token分割器"""
        try:
            if self.config.tokenizer_name == "tiktoken":
                return MarkdownTextSplitter.from_tiktoken_encoder(
                    encoding_name=self.config.encoding_name,
                    chunk_size=self.config.chunk_size,
                    chunk_overlap=self.config.chunk_overlap,
                    keep_separator=self.config.keep_separator,
                )
            else:
                logger.info(f"加载HuggingFace tokenizer: {self.config.encoding_name}")
                tokenizer = AutoTokenizer.from_pretrained(
                    self.config.encoding_name, trust_remote_code=True
                )
                return MarkdownTextSplitter.from_huggingface_tokenizer(
                    tokenizer=tokenizer,
                    chunk_size=self.config.chunk_size,
                    chunk_overlap=self.config.chunk_overlap,
                )
        except Exception as e:
            logger.error(f"Tokenizer初始化失败: {e}")
            raise ValueError(
                f"无法初始化tokenizer '{self.config.encoding_name}': {e}"
            ) from e

    def split(
        self, docs: List[Document], show_progress: bool = False
    ) -> List[Document]:
        """分割文档

        Args:
            docs: 待分割的文档列表
            show_progress: 是否显示进度条

        Returns:
            分割后的文档列表

        Raises:
            ValueError: 当文档列表为空时
        """
        if not docs:
            raise ValueError("文档列表不能为空")

        logger.info(f"开始分割 {len(docs)} 个文档")
        split_docs: List[Document] = []

        # 可选进度条支持
        iterator = docs
        if show_progress:
            try:
                iterator = tqdm(docs, desc="分割文档")  # type: ignore
            except ImportError:
                logger.warning("tqdm未安装，无法显示进度条")

        for doc in iterator:
            try:
                # 第一步：按标题分割
                header_docs = self._header_splitter.split_text(doc.page_content)

                # 保留原始元数据
                header_docs_with_metadata = [
                    Document(
                        page_content=header_doc.page_content,
                        metadata={**doc.metadata, "split_level": "header"},
                    )
                    for header_doc in header_docs
                ]

                # 第二步：按token分割
                final_docs = self._token_splitter.split_documents(
                    header_docs_with_metadata
                )

                # 添加分块索引信息
                for idx, final_doc in enumerate(final_docs):
                    final_doc.metadata.update(
                        {
                            "split_level": "token",
                            "chunk_index": idx,
                            "total_chunks": len(final_docs),
                        }
                    )

                split_docs.extend(final_docs)

            except Exception as e:
                logger.error(
                    f"文档分割失败: {doc.metadata.get('source', 'unknown')} - {e}"
                )
                # 继续处理下一个文档
                continue

        logger.info(f"分割完成，生成 {len(split_docs)} 个文档块")
        return split_docs

    def split_text(self, text: str, metadata: Optional[dict] = None) -> List[Document]:
        """直接分割文本

        Args:
            text: 待分割的文本
            metadata: 可选的元数据

        Returns:
            分割后的文档列表
        """
        doc = Document(page_content=text, metadata=metadata or {})
        return self.split([doc])


if __name__ == "__main__":
    from doc.loader.doc_loader import DocLoader

    loader = DocLoader(
        "url",
        [
            "https://lilianweng.github.io/posts/2023-06-23-agent/",  # AI代理相关文章
            # "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",  # 提示工程文章
            # "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",  # LLM对抗攻击文章
        ],
    )
    docs, error_urls = loader.load()
    # print(len(docs))
    # print(len(error_urls))
    # print(len(docs[0].page_content))
    # md_splitter = MdSplitter(
    #     headers=[
    #         ("#", "Header 1"),
    #         ("##", "Header 2"),
    #         ("###", "Header 3"),
    #         ("####", "Header 4"),
    #         ("#####", "Header 5"),
    #         ("######", "Header 6"),
    #     ],
    #     tokenizer_name="huggingface",
    #     encoding_name="Qwen/Qwen-7B-Chat",
    #     chunk_size=1000,
    #     chunk_overlap=200,
    #     keep_separator=True,
    # )
    md_splitter = MdSplitter(
        headers=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5"),
            ("######", "Header 6"),
        ],
        tokenizer_name="tiktoken",
        encoding_name="cl100k_base",
        chunk_size=1000,
        chunk_overlap=200,
        keep_separator=True,
    )
    result = md_splitter.split(docs)
    print(len(result))
