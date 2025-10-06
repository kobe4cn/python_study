"""
LLM提供商插件系统
支持动态注册和加载不同的LLM提供商
"""

from llm.providers.registry import LLMRegistry
from llm.providers.qwen import QwenProvider

# 注册内置提供商
LLMRegistry.register("qwen", QwenProvider)

__all__ = ["LLMRegistry"]
