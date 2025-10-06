"""
测试LLM提供商注册中心
"""

import pytest
from llm.providers.registry import LLMRegistry
from llm.providers.qwen import QwenProvider
from llm.base import BaseLlmModel


class MockProvider(BaseLlmModel):
    """Mock LLM提供商用于测试"""

    def __init__(self, **kwargs):
        self.config = kwargs

    def llm_json_response(self, system_prompt: str, human_prompt: str):
        return '{"mock": "response"}'

    def llm_chat_response(self, system_prompt: str, human_prompt: str):
        return "Mock response"

    def llm_chat_response_by_human_prompt(self, human_prompt: str):
        return "Mock response"


class TestLLMRegistry:
    """测试LLM注册中心"""

    def setup_method(self):
        """每个测试方法前执行"""
        # 清空注册表和缓存
        LLMRegistry._providers.clear()
        LLMRegistry._instances.clear()

    def test_register_provider(self):
        """测试注册提供商"""
        LLMRegistry.register("mock", MockProvider)

        assert LLMRegistry.is_registered("mock")
        assert "mock" in LLMRegistry.list_providers()

    def test_register_invalid_provider(self):
        """测试注册无效提供商"""

        class InvalidProvider:
            pass

        with pytest.raises(TypeError):
            LLMRegistry.register("invalid", InvalidProvider)

    def test_unregister_provider(self):
        """测试注销提供商"""
        LLMRegistry.register("mock", MockProvider)
        assert LLMRegistry.is_registered("mock")

        LLMRegistry.unregister("mock")
        assert not LLMRegistry.is_registered("mock")

    def test_create_instance(self):
        """测试创建实例"""
        LLMRegistry.register("mock", MockProvider)

        instance = LLMRegistry.create(
            "mock", model="test-model", api_key="test-key"
        )

        assert isinstance(instance, MockProvider)
        assert instance.config["model"] == "test-model"
        assert instance.config["api_key"] == "test-key"

    def test_create_unregistered_provider(self):
        """测试创建未注册的提供商"""
        with pytest.raises(KeyError) as exc_info:
            LLMRegistry.create("nonexistent")

        assert "未注册" in str(exc_info.value)

    def test_instance_caching(self):
        """测试实例缓存"""
        LLMRegistry.register("mock", MockProvider)

        # 创建两个相同参数的实例
        instance1 = LLMRegistry.create("mock", cache=True, model="test")
        instance2 = LLMRegistry.create("mock", cache=True, model="test")

        # 应该是同一个实例
        assert instance1 is instance2

    def test_instance_no_caching(self):
        """测试禁用缓存"""
        LLMRegistry.register("mock", MockProvider)

        # 创建两个相同参数的实例,但禁用缓存
        instance1 = LLMRegistry.create("mock", cache=False, model="test")
        instance2 = LLMRegistry.create("mock", cache=False, model="test")

        # 应该是不同的实例
        assert instance1 is not instance2

    def test_list_providers(self):
        """测试列出提供商"""
        LLMRegistry.register("mock1", MockProvider)
        LLMRegistry.register("mock2", MockProvider)

        providers = LLMRegistry.list_providers()

        assert "mock1" in providers
        assert "mock2" in providers
        assert len(providers) == 2

    def test_get_provider_class(self):
        """测试获取提供商类"""
        LLMRegistry.register("mock", MockProvider)

        provider_class = LLMRegistry.get_provider_class("mock")

        assert provider_class is MockProvider

    def test_get_provider_info(self):
        """测试获取提供商信息"""
        LLMRegistry.register("mock", MockProvider)

        info = LLMRegistry.get_provider_info()

        assert "mock" in info
        assert info["mock"]["class_name"] == "MockProvider"
        assert "module" in info["mock"]

    def test_clear_cache(self):
        """测试清空缓存"""
        LLMRegistry.register("mock", MockProvider)

        # 创建缓存实例
        instance1 = LLMRegistry.create("mock", cache=True, model="test")

        # 清空缓存
        LLMRegistry.clear_cache()

        # 再次创建应该是新实例
        instance2 = LLMRegistry.create("mock", cache=True, model="test")

        assert instance1 is not instance2

    def test_qwen_provider_registration(self):
        """测试Qwen提供商是否正确注册"""
        from llm.providers import LLMRegistry as ImportedRegistry

        assert ImportedRegistry.is_registered("qwen")

        provider_class = ImportedRegistry.get_provider_class("qwen")
        assert provider_class is QwenProvider
