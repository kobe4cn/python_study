"""
测试依赖注入容器
"""

import pytest
from unittest.mock import Mock, patch
from core.container import Container, get_container
from core.config import AppSettings


class TestContainer:
    """测试依赖注入容器"""

    def test_container_initialization(self, test_config):
        """测试容器初始化"""
        container = Container(test_config)

        assert container.settings == test_config
        assert container._llm is None
        assert container._tools is None

    def test_get_llm_default(self, test_container):
        """测试获取默认LLM"""
        # 因为需要真实的API,这里只测试调用不会抛出异常
        # 实际的LLM功能测试应该mock
        with pytest.raises(Exception):
            # 预期会失败,因为test-api-key不是真实key
            llm = test_container.get_llm()

    @patch("core.container.LLMRegistry.create")
    def test_get_llm_mocked(self, mock_create, test_container, mock_llm):
        """测试获取LLM(使用mock)"""
        mock_create.return_value = mock_llm

        llm = test_container.get_llm()

        assert llm == mock_llm
        mock_create.assert_called_once()

    @patch("core.container.LLMRegistry.create")
    def test_get_llm_custom_params(self, mock_create, test_container, mock_llm):
        """测试使用自定义参数获取LLM"""
        mock_create.return_value = mock_llm

        llm = test_container.get_llm(
            provider="qwen", model="custom-model", temperature=0.8
        )

        # 验证调用参数
        call_args = mock_create.call_args
        assert call_args[0][0] == "qwen"  # provider
        assert call_args[1]["model"] == "custom-model"
        assert call_args[1]["temperature"] == 0.8

    def test_get_tools(self, test_container):
        """测试获取工具"""
        tools = test_container.get_tools()

        # 验证工具已创建
        assert tools is not None

        # 再次获取应该返回同一个实例
        tools2 = test_container.get_tools()
        assert tools is tools2

    def test_get_graph_dependencies(self, test_container):
        """测试获取Graph依赖"""
        with patch.object(test_container, "get_llm") as mock_llm, patch.object(
            test_container, "get_tools"
        ) as mock_tools, patch.object(
            test_container, "get_retriever"
        ) as mock_retriever:

            deps = test_container.get_graph_dependencies()

            assert "llm" in deps
            assert "tools" in deps
            assert "retriever" in deps
            mock_llm.assert_called_once()
            mock_tools.assert_called_once()
            mock_retriever.assert_called_once()

    def test_reset_container(self, test_container):
        """测试重置容器"""
        # 创建一些依赖
        tools = test_container.get_tools()
        assert test_container._tools is not None

        # 重置
        test_container.reset()

        # 验证依赖已清除
        assert test_container._llm is None
        assert test_container._tools is None
        assert test_container._retriever is None

    def test_get_container_singleton(self):
        """测试容器单例"""
        container1 = get_container()
        container2 = get_container()

        # 应该是同一个实例
        assert container1 is container2
