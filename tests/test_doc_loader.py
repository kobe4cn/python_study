"""DocLoader 单元测试"""

import pytest
from pathlib import Path
from doc.loader.doc_loader import DocLoader, DocLoaderConfig, LoadError


class TestDocLoaderConfig:
    """DocLoaderConfig 测试"""

    def test_config_validation_url(self):
        """测试URL配置验证"""
        config = DocLoaderConfig(
            doc_type="url",
            doc_paths=["https://example.com"]
        )
        assert config.doc_type == "url"
        assert len(config.doc_paths) == 1

    def test_config_validation_invalid_url(self):
        """测试无效URL"""
        with pytest.raises(ValueError, match="无效的URL格式"):
            DocLoaderConfig(
                doc_type="url",
                doc_paths=["not_a_url"]
            )

    def test_config_validation_empty_paths(self):
        """测试空路径列表"""
        with pytest.raises(ValueError):
            DocLoaderConfig(doc_type="url", doc_paths=[])

    def test_config_validation_file_type(self):
        """测试文件类型配置"""
        config = DocLoaderConfig(
            doc_type="file",
            doc_paths=["/path/to/file.txt"]
        )
        assert config.doc_type == "file"


class TestDocLoader:
    """DocLoader 测试"""

    def test_init_with_url(self):
        """测试URL初始化"""
        loader = DocLoader(
            doc_type="url",
            doc_path=["https://example.com"]
        )
        assert loader.config.doc_type == "url"

    def test_init_with_file(self):
        """测试文件初始化"""
        loader = DocLoader(
            doc_type="file",
            doc_path=["/path/to/file.txt"]
        )
        assert loader.config.doc_type == "file"

    def test_load_file_not_exists(self):
        """测试加载不存在的文件"""
        loader = DocLoader(
            doc_type="file",
            doc_path=["/path/to/nonexistent/file.txt"]
        )
        docs, errors = loader.load()
        assert len(docs) == 0
        assert len(errors) == 1
        assert isinstance(errors[0], LoadError)
        assert errors[0].error_type == "FileNotFoundError"

    @pytest.mark.integration
    def test_load_url_success(self):
        """测试URL加载成功（集成测试）"""
        loader = DocLoader(
            doc_type="url",
            doc_path=["https://example.com"]
        )
        docs, errors = loader.load()
        # 注意：这个测试需要网络连接
        assert isinstance(docs, list)
        assert isinstance(errors, list)

    def test_load_error_str_representation(self):
        """测试LoadError的字符串表示"""
        error = LoadError(
            file_path="/test/file.txt",
            error=Exception("测试错误"),
            error_type="TestError"
        )
        error_str = str(error)
        assert "/test/file.txt" in error_str
        assert "TestError" in error_str
        assert "测试错误" in error_str
