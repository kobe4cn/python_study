"""
通义千问(Qwen)LLM提供商
基于原有QwenMain实现,符合插件化架构
"""

from __future__ import annotations

import logging
from typing import Optional

from llm.base import BaseLlmModel
from llm.qwen import QwenMain

logger = logging.getLogger(__name__)


class QwenProvider(BaseLlmModel):
    """
    通义千问LLM提供商

    封装QwenMain,使其符合插件化架构的接口规范。

    Example:
        >>> provider = QwenProvider(
        ...     model="qwen3-max",
        ...     api_key="your-api-key",
        ...     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        ...     temperature=0.5
        ... )
        >>> response = provider.llm_chat_response(
        ...     system_prompt="你是一位助手",
        ...     human_prompt="你好"
        ... )
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str,
        temperature: float = 0.5,
        stream: bool = True,
        formats: Optional[str] = None,
    ):
        """
        初始化Qwen提供商

        Args:
            model: 模型名称(如qwen3-max)
            api_key: API密钥
            base_url: API基础URL
            temperature: 温度参数(0.0-2.0)
            stream: 是否流式输出
            formats: 输出格式("json"或None)
        """
        self._qwen = QwenMain(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            stream=stream,
            formats=formats,
        )
        logger.info(f"QwenProvider initialized with model: {model}")

    def llm_json_response(self, system_prompt: str, human_prompt: str):
        """
        获取JSON格式响应

        Args:
            system_prompt: 系统提示词
            human_prompt: 用户提示词

        Returns:
            JSON格式响应
        """
        return self._qwen.llm_json_response(system_prompt, human_prompt)

    def llm_chat_response(self, system_prompt: str, human_prompt: str):
        """
        获取聊天格式响应

        Args:
            system_prompt: 系统提示词
            human_prompt: 用户提示词

        Returns:
            聊天响应
        """
        return self._qwen.llm_chat_response(system_prompt, human_prompt)

    def llm_chat_response_by_human_prompt(self, human_prompt: str):
        """
        仅使用用户提示词获取响应

        Args:
            human_prompt: 用户提示词

        Returns:
            聊天响应
        """
        return self._qwen.llm_chat_response_by_human_prompt(human_prompt)
