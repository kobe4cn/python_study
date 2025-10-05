"""MdSplitter 单元测试"""

import pytest
from doc.spliter.md_splitter import MdSplitter, SplitterConfig
from langchain_core.documents import Document


class TestSplitterConfig:
    """SplitterConfig 测试"""

    def test_config_validation(self):
        """测试配置验证"""
        config = SplitterConfig(
            tokenizer_name="tiktoken",
            encoding_name="cl100k_base",
            chunk_size=1000,
            chunk_overlap=200
        )
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200

    def test_config_invalid_overlap(self):
        """测试无效的重叠大小"""
        with pytest.raises(ValueError, match="chunk_overlap .* 必须小于 chunk_size"):
            SplitterConfig(
                tokenizer_name="tiktoken",
                encoding_name="cl100k_base",
                chunk_size=100,
                chunk_overlap=200  # 大于chunk_size
            )

    def test_config_overlap_equal_to_chunk_size(self):
        """测试重叠大小等于块大小"""
        with pytest.raises(ValueError):
            SplitterConfig(
                tokenizer_name="tiktoken",
                encoding_name="cl100k_base",
                chunk_size=100,
                chunk_overlap=100
            )

    def test_config_default_headers(self):
        """测试默认标题配置"""
        config = SplitterConfig(
            tokenizer_name="tiktoken",
            encoding_name="cl100k_base",
            chunk_size=1000,
            chunk_overlap=200
        )
        assert len(config.headers) == 6
        assert config.headers[0] == ("#", "Header 1")


class TestMdSplitter:
    """MdSplitter 测试"""

    def test_init_with_tiktoken(self):
        """测试使用tiktoken初始化"""
        splitter = MdSplitter(
            headers=[("#", "H1"), ("##", "H2")],
            tokenizer_name="tiktoken",
            encoding_name="cl100k_base",
            chunk_size=100,
            chunk_overlap=10
        )
        assert splitter.config.tokenizer_name == "tiktoken"

    def test_split_empty_docs(self):
        """测试空文档列表"""
        splitter = MdSplitter(
            headers=[("#", "H1")],
            tokenizer_name="tiktoken",
            encoding_name="cl100k_base",
            chunk_size=100,
            chunk_overlap=10
        )
        with pytest.raises(ValueError, match="文档列表不能为空"):
            splitter.split([])

    def test_split_with_metadata(self):
        """测试元数据保留"""
        splitter = MdSplitter(
            headers=[("#", "H1")],
            tokenizer_name="tiktoken",
            encoding_name="cl100k_base",
            chunk_size=1000,
            chunk_overlap=100
        )
        doc = Document(
            page_content="# Title\n\nThis is some content.",
            metadata={"source": "test.md", "author": "Test"}
        )
        result = splitter.split([doc])

        # 验证所有分块都包含原始元数据
        assert all("source" in d.metadata for d in result)
        assert all("author" in d.metadata for d in result)
        # 验证添加了新元数据
        assert all("split_level" in d.metadata for d in result)
        assert all("chunk_index" in d.metadata for d in result)

    def test_split_text_method(self):
        """测试直接文本分割方法"""
        splitter = MdSplitter(
            headers=[("#", "H1")],
            tokenizer_name="tiktoken",
            encoding_name="cl100k_base",
            chunk_size=100,
            chunk_overlap=10
        )
        text = "# Title\n\nContent here"
        metadata = {"source": "test"}

        result = splitter.split_text(text, metadata)

        assert len(result) > 0
        assert all(isinstance(d, Document) for d in result)
        assert all(d.metadata.get("source") == "test" for d in result)

    @pytest.mark.slow
    def test_split_with_progress(self):
        """测试带进度条的分割（需要tqdm）"""
        try:
            import tqdm
            splitter = MdSplitter(
                headers=[("#", "H1")],
                tokenizer_name="tiktoken",
                encoding_name="cl100k_base",
                chunk_size=100,
                chunk_overlap=10
            )
            doc = Document(
                page_content="# Title\n\nContent",
                metadata={}
            )
            # 测试不应该抛出异常
            result = splitter.split([doc], show_progress=True)
            assert len(result) > 0
        except ImportError:
            pytest.skip("tqdm not installed")
