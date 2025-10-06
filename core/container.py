"""
依赖注入容器
管理应用的所有依赖,支持依赖注入和单例模式
"""

from __future__ import annotations

import logging
from typing import Optional, Any, Dict
from functools import lru_cache

from llm.providers import LLMRegistry
from llm.base import BaseLlmModel
from core.config import AppSettings, get_settings

logger = logging.getLogger(__name__)


class Container:
    """
    依赖注入容器

    管理应用的所有依赖项,包括LLM、检索器、工具等。
    使用单例模式确保依赖项只创建一次。

    Example:
        >>> from core.container import get_container
        >>>
        >>> # 获取容器
        >>> container = get_container()
        >>>
        >>> # 获取LLM实例
        >>> llm = container.get_llm()
        >>> response = llm.llm_chat_response(
        ...     system_prompt="你是助手",
        ...     human_prompt="你好"
        ... )
        >>>
        >>> # 获取工具
        >>> tools = container.get_tools()
        >>> results = tools.tavily_search("最新新闻")
    """

    def __init__(self, settings: Optional[AppSettings] = None):
        """
        初始化容器

        Args:
            settings: 应用配置,如果为None则使用默认配置
        """
        self.settings = settings or get_settings()
        self._llm: Optional[BaseLlmModel] = None
        self._tools: Optional[Any] = None
        self._retriever: Optional[Any] = None

        logger.info("依赖注入容器已初始化")

    def get_llm(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> BaseLlmModel:
        """
        获取LLM实例

        Args:
            provider: LLM提供商名称,如果为None则使用配置中的默认值
            model: 模型名称,如果为None则使用配置中的默认值
            **kwargs: 其他LLM参数,会覆盖配置中的值

        Returns:
            LLM实例

        Example:
            >>> container = get_container()
            >>>
            >>> # 使用默认配置
            >>> llm = container.get_llm()
            >>>
            >>> # 自定义提供商和模型
            >>> llm = container.get_llm(
            ...     provider="qwen",
            ...     model="qwen3-max",
            ...     temperature=0.7
            ... )
        """
        # 使用配置中的默认值
        provider = provider or self.settings.llm.provider
        model = model or self.settings.llm.model

        # 准备LLM参数
        llm_params = {
            "model": model,
            "api_key": self.settings.llm.api_key,
            "base_url": self.settings.llm.base_url,
            "temperature": self.settings.llm.temperature,
            "stream": self.settings.llm.stream,
        }

        # 覆盖自定义参数
        llm_params.update(kwargs)

        # 从注册中心创建实例
        return LLMRegistry.create(provider, cache=True, **llm_params)

    def get_tools(self):
        """
        获取工具实例

        Returns:
            UdfTools实例

        Example:
            >>> tools = container.get_tools()
            >>> results = tools.tavily_search("人工智能")
        """
        if self._tools is None:
            from tools.udf_tools import UdfTools
            self._tools = UdfTools()
            logger.info("工具实例已创建")

        return self._tools

    def get_retriever(
        self,
        collection_name: Optional[str] = None,
        top_k: Optional[int] = None
    ):
        """
        获取检索器实例

        Args:
            collection_name: 集合名称,如果为None则使用配置中的默认值
            top_k: 返回结果数量,如果为None则使用配置中的默认值

        Returns:
            检索器实例

        Example:
            >>> retriever = container.get_retriever()
            >>> docs = retriever.invoke("搜索查询")
        """
        # TODO: 实现通用检索器工厂
        # 支持多种向量数据库(Qdrant/Pinecone/Weaviate)
        logger.warning("get_retriever 方法尚未完全实现")
        return None

    def get_graph_dependencies(self) -> Dict[str, Any]:
        """
        获取Graph工作流所需的所有依赖

        Returns:
            包含llm、tools、retriever的字典

        Example:
            >>> deps = container.get_graph_dependencies()
            >>> graph = GraphMain(**deps)
        """
        return {
            "llm": self.get_llm(),
            "tools": self.get_tools(),
            "retriever": self.get_retriever(),
        }

    def reset(self) -> None:
        """
        重置容器,清除所有缓存的依赖

        Example:
            >>> container.reset()
        """
        self._llm = None
        self._tools = None
        self._retriever = None
        LLMRegistry.clear_cache()
        logger.info("容器已重置")


@lru_cache()
def get_container(settings: Optional[AppSettings] = None) -> Container:
    """
    获取全局容器单例

    Args:
        settings: 应用配置

    Returns:
        Container实例

    Example:
        >>> from core.container import get_container
        >>> container = get_container()
        >>> llm = container.get_llm()
    """
    return Container(settings)


# 全局容器实例
container = get_container()


if __name__ == "__main__":
    import os
    import dotenv

    dotenv.load_dotenv()

    print("=" * 60)
    print("依赖注入容器测试")
    print("=" * 60)

    # 获取容器
    container = get_container()

    print("\n1. 测试LLM实例获取:")
    try:
        llm = container.get_llm()
        print(f"  ✓ LLM实例创建成功: {type(llm).__name__}")
    except Exception as e:
        print(f"  ✗ LLM实例创建失败: {e}")

    print("\n2. 测试工具实例获取:")
    try:
        tools = container.get_tools()
        print(f"  ✓ 工具实例创建成功: {type(tools).__name__}")
    except Exception as e:
        print(f"  ✗ 工具实例创建失败: {e}")

    print("\n3. 测试依赖复用:")
    llm2 = container.get_llm()
    print(f"  同一实例: {llm is llm2}")

    print("\n" + "=" * 60)
