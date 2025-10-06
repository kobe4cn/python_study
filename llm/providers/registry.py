"""
LLM提供商注册中心
实现插件化的LLM提供商管理
"""

from __future__ import annotations

import logging
from typing import Dict, Type, Any, Optional

from llm.base import BaseLlmModel

logger = logging.getLogger(__name__)


class LLMRegistry:
    """
    LLM提供商注册中心

    使用注册表模式管理LLM提供商,支持动态注册和获取。

    Example:
        >>> from llm.providers import LLMRegistry, QwenProvider
        >>>
        >>> # 注册提供商
        >>> LLMRegistry.register("qwen", QwenProvider)
        >>>
        >>> # 创建LLM实例
        >>> llm = LLMRegistry.create(
        ...     "qwen",
        ...     model="qwen3-max",
        ...     api_key="your-api-key",
        ...     base_url="https://...",
        ...     temperature=0.5
        ... )
        >>>
        >>> # 列出所有注册的提供商
        >>> providers = LLMRegistry.list_providers()
        >>> print(providers)  # ['qwen', 'openai', ...]
    """

    _providers: Dict[str, Type[BaseLlmModel]] = {}
    _instances: Dict[str, BaseLlmModel] = {}

    @classmethod
    def register(cls, name: str, provider_class: Type[BaseLlmModel]) -> None:
        """
        注册LLM提供商

        Args:
            name: 提供商名称(如'qwen', 'openai')
            provider_class: 提供商类,必须继承BaseLlmModel

        Raises:
            TypeError: 如果provider_class不是BaseLlmModel的子类
            ValueError: 如果提供商名称已存在

        Example:
            >>> from llm.providers.qwen import QwenProvider
            >>> LLMRegistry.register("qwen", QwenProvider)
        """
        if not issubclass(provider_class, BaseLlmModel):
            raise TypeError(
                f"{provider_class.__name__} 必须继承 BaseLlmModel"
            )

        if name in cls._providers:
            logger.warning(f"提供商 '{name}' 已存在,将被覆盖")

        cls._providers[name] = provider_class
        logger.info(f"已注册LLM提供商: {name} -> {provider_class.__name__}")

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        注销LLM提供商

        Args:
            name: 提供商名称

        Example:
            >>> LLMRegistry.unregister("qwen")
        """
        if name in cls._providers:
            del cls._providers[name]
            logger.info(f"已注销LLM提供商: {name}")

        # 清理缓存的实例
        if name in cls._instances:
            del cls._instances[name]

    @classmethod
    def create(
        cls,
        name: str,
        cache: bool = True,
        **kwargs: Any
    ) -> BaseLlmModel:
        """
        创建LLM实例

        Args:
            name: 提供商名称
            cache: 是否缓存实例(默认True),缓存后相同参数会返回同一实例
            **kwargs: 提供商初始化参数

        Returns:
            LLM实例

        Raises:
            KeyError: 如果提供商未注册
            Exception: 实例化失败时抛出

        Example:
            >>> llm = LLMRegistry.create(
            ...     "qwen",
            ...     model="qwen3-max",
            ...     api_key="sk-xxx",
            ...     temperature=0.5
            ... )
        """
        if name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise KeyError(
                f"LLM提供商 '{name}' 未注册. "
                f"可用提供商: {available}"
            )

        # 如果启用缓存且实例已存在,直接返回
        cache_key = f"{name}:{str(sorted(kwargs.items()))}"
        if cache and cache_key in cls._instances:
            logger.debug(f"返回缓存的LLM实例: {name}")
            return cls._instances[cache_key]

        # 创建新实例
        try:
            provider_class = cls._providers[name]
            instance = provider_class(**kwargs)

            if cache:
                cls._instances[cache_key] = instance

            logger.info(f"创建LLM实例: {name} ({provider_class.__name__})")
            return instance

        except Exception as e:
            logger.error(f"创建LLM实例失败: {name} - {e}")
            raise

    @classmethod
    def get_provider_class(cls, name: str) -> Type[BaseLlmModel]:
        """
        获取提供商类

        Args:
            name: 提供商名称

        Returns:
            提供商类

        Raises:
            KeyError: 如果提供商未注册

        Example:
            >>> provider_class = LLMRegistry.get_provider_class("qwen")
            >>> print(provider_class.__name__)  # QwenProvider
        """
        if name not in cls._providers:
            raise KeyError(f"LLM提供商 '{name}' 未注册")

        return cls._providers[name]

    @classmethod
    def list_providers(cls) -> list[str]:
        """
        列出所有注册的提供商

        Returns:
            提供商名称列表

        Example:
            >>> providers = LLMRegistry.list_providers()
            >>> print(providers)  # ['qwen', 'openai', 'anthropic']
        """
        return list(cls._providers.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        检查提供商是否已注册

        Args:
            name: 提供商名称

        Returns:
            是否已注册

        Example:
            >>> if LLMRegistry.is_registered("qwen"):
            ...     print("Qwen is available")
        """
        return name in cls._providers

    @classmethod
    def clear_cache(cls) -> None:
        """
        清空实例缓存

        Example:
            >>> LLMRegistry.clear_cache()
        """
        cls._instances.clear()
        logger.info("已清空LLM实例缓存")

    @classmethod
    def get_provider_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有提供商信息

        Returns:
            提供商信息字典

        Example:
            >>> info = LLMRegistry.get_provider_info()
            >>> for name, details in info.items():
            ...     print(f"{name}: {details['class_name']}")
        """
        return {
            name: {
                "class_name": provider_class.__name__,
                "module": provider_class.__module__,
                "doc": provider_class.__doc__,
            }
            for name, provider_class in cls._providers.items()
        }


if __name__ == "__main__":
    # 测试注册中心
    print("=" * 60)
    print("LLM Provider Registry 测试")
    print("=" * 60)

    # 列出提供商
    providers = LLMRegistry.list_providers()
    print(f"\n已注册的提供商: {providers}")

    # 获取提供商信息
    info = LLMRegistry.get_provider_info()
    print("\n提供商详情:")
    for name, details in info.items():
        print(f"  {name}:")
        print(f"    类名: {details['class_name']}")
        print(f"    模块: {details['module']}")
