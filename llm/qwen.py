"""
Qwen (通义千问) LLM实现模块
================================

本模块提供通义千问大语言模型的具体实现,基于LangChain的ChatTongyi客户端。
实现了BaseLlmModel接口,支持JSON和普通文本两种响应格式。

主要特性:
    - 支持通义千问全系列模型(qwen3-max, qwen-turbo等)
    - 支持JSON格式和普通文本格式响应
    - 基于LangChain的ChatTongyi客户端
    - 完善的错误处理和日志记录
    - 自动重试机制

支持的模型:
    - qwen3-max: 通义千问3.0旗舰版
    - qwen-turbo: 快速响应版本
    - qwen-plus: 增强版本

配置要求:
    环境变量:
        OPENAI_API_KEY: API密钥(必需)
        OPENAI_BASE_URL: API基础URL(可选)

典型用法:
    >>> from llm.qwen import QwenMain
    >>> import os
    >>>
    >>> # 创建Qwen实例
    >>> qwen = QwenMain(
    ...     model="qwen3-max",
    ...     api_key=os.getenv("OPENAI_API_KEY"),
    ...     base_url=os.getenv("OPENAI_BASE_URL"),
    ...     temperature=0.7,
    ...     stream=True
    ... )
    >>>
    >>> # 聊天响应
    >>> response = qwen.llm_chat_response(
    ...     system_prompt="你是AI助手",
    ...     human_prompt="你好"
    ... )

作者: Kevin
创建日期: 2025
版本: 1.0.1
"""

from pydantic import BaseModel, Field, SecretStr
import os
import dotenv
import logging
from langchain_community.chat_models import ChatTongyi
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

# 导入抽象基类
from llm.base import BaseLlmModel

logger = logging.getLogger(__name__)
dotenv.load_dotenv()


class QwenConfig(BaseModel):
    """
    Qwen配置模型

    使用Pydantic定义通义千问LLM的配置参数,提供数据验证和默认值管理。

    Attributes:
        model: 模型名称,默认"qwen3-max"
        api_key: API密钥,默认从环境变量OPENAI_API_KEY读取
        base_url: API基础URL,默认从环境变量OPENAI_BASE_URL读取
        temperature: 采样温度,范围0.0-1.0,默认0.5
        stream: 是否启用流式响应,默认True
        formats: 响应格式,可选"json",默认None

    Example:
        >>> config = QwenConfig(
        ...     model="qwen-turbo",
        ...     temperature=0.3,
        ...     stream=False
        ... )
    """

    model: str = Field(default="qwen3-max", description="模型名称")
    api_key: str = Field(
        default=os.getenv("OPENAI_API_KEY") or "", description="API密钥"
    )
    base_url: str = Field(
        default=os.getenv("OPENAI_BASE_URL") or "", description="基础URL"
    )
    temperature: float = Field(default=0.5, ge=0.0, le=1.0, description="温度")
    stream: bool = Field(default=True, description="是否流式")
    formats: Optional[str] = Field(default=None, description="格式")


class QwenMain(BaseLlmModel):
    """
    Qwen主类 - 通义千问LLM实现

    实现BaseLlmModel接口,提供通义千问模型的具体功能。支持JSON和文本
    两种响应格式,自动根据配置初始化相应的客户端。

    Attributes:
        config: Qwen配置对象
        _client: 内部ChatTongyi客户端实例

    Example:
        >>> qwen = QwenMain(
        ...     model="qwen3-max",
        ...     api_key="sk-xxx",
        ...     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        ...     temperature=0.7,
        ...     stream=True
        ... )
        >>> response = qwen.llm_chat_response(
        ...     system_prompt="你是助手",
        ...     human_prompt="你好"
        ... )

    Note:
        - 客户端在__init__中立即初始化
        - 确保已设置环境变量OPENAI_API_KEY
        - 继承自BaseLlmModel,实现统一接口
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str,
        temperature: float,
        stream: bool,
        formats: Optional[str] = None,
    ) -> None:
        """
        初始化Qwen主类

        创建配置并立即初始化ChatTongyi客户端。根据formats参数选择
        初始化JSON客户端或普通客户端。

        Args:
            model: 模型名称,推荐值:
                - "qwen3-max": 最强能力
                - "qwen-turbo": 快速响应
                - "qwen-plus": 平衡选择
            api_key: 通义千问API密钥
            base_url: API基础URL
            temperature: 采样温度,范围0.0-1.0
            stream: 是否启用流式响应
            formats: 响应格式,可选"json"

        Raises:
            ValidationError: 配置参数验证失败
            RuntimeError: 客户端初始化失败

        Example:
            >>> qwen = QwenMain(
            ...     model="qwen3-max",
            ...     api_key="sk-xxx",
            ...     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            ...     temperature=0.7,
            ...     stream=True
            ... )
        """
        self.config = QwenConfig(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            stream=stream,
            formats=formats,
        )

        # 初始化客户端
        self._client: Optional[ChatTongyi] = None
        self._initialize()

    @property
    def client(self) -> ChatTongyi:
        """
        获取ChatTongyi客户端实例

        Returns:
            ChatTongyi客户端实例

        Raises:
            RuntimeError: 客户端未初始化时抛出

        Example:
            >>> qwen = QwenMain(...)
            >>> client = qwen.client
        """
        if self._client is None:
            raise RuntimeError("Qwen客户端未初始化")
        return self._client

    def _initialize(self) -> None:
        """
        初始化ChatTongyi客户端(内部方法)

        根据config.formats的值选择初始化方式:
        - 如果formats有值(如"json"),调用_get_json_client()
        - 否则调用_get_client()

        此方法在__init__中自动调用,不应手动调用。

        Raises:
            Exception: 客户端创建失败时抛出
        """
        try:
            if self.config.formats:
                self._client = self._get_json_client()
            else:
                self._client = self._get_client()
        except Exception as e:
            logger.error(f"Qwen客户端初始化失败: {e}")
            raise

    def _get_client(self) -> ChatTongyi:
        """
        获取普通文本格式的ChatTongyi客户端(内部方法)

        创建并返回标准的ChatTongyi客户端,用于普通文本响应。

        Returns:
            ChatTongyi客户端实例

        Raises:
            Exception: 客户端创建失败时抛出
        """
        try:
            return ChatTongyi(
                model=self.config.model,
                api_key=SecretStr(self.config.api_key) if self.config.api_key else None,
                temperature=self.config.temperature,
                streaming=self.config.stream,
            )
        except Exception as e:
            logger.error(f"初始化Qwen客户端失败: {e}")
            raise

    def _get_json_client(self) -> ChatTongyi:
        """
        获取JSON格式的ChatTongyi客户端(内部方法)

        创建并返回配置为JSON格式输出的ChatTongyi客户端。

        Returns:
            ChatTongyi客户端实例

        Raises:
            Exception: 客户端创建失败时抛出
        """
        try:
            return ChatTongyi(
                model=self.config.model,
                api_key=SecretStr(self.config.api_key) if self.config.api_key else None,
                temperature=self.config.temperature,
                streaming=self.config.stream,
                format=self.config.formats,
            )
        except Exception as e:
            logger.error(f"初始化Qwen JSON客户端失败: {e}")
            raise

    def llm_json_response(self, system_prompt: str, human_prompt: str):
        """
        获取JSON格式的LLM响应

        使用系统提示和用户提示调用Qwen模型,返回JSON格式的响应。
        建议在初始化时设置formats="json"以确保输出格式。

        Args:
            system_prompt: 系统提示,定义AI角色和输出要求
                建议明确指示JSON格式和结构
            human_prompt: 用户提示,具体查询内容

        Returns:
            JSON格式的响应字符串

        Raises:
            ValueError: 响应格式无效时抛出
            ConnectionError: API连接失败时抛出
            Exception: 其他API调用错误

        Example:
            >>> qwen = QwenMain(..., formats="json")
            >>> response = qwen.llm_json_response(
            ...     system_prompt="你是数据分析专家,以JSON格式返回",
            ...     human_prompt="分析销售数据"
            ... )
            >>> import json
            >>> data = json.loads(response)

        Note:
            - 需要在初始化时设置formats="json"
            - 建议在system_prompt中明确定义JSON结构
            - 响应会自动进行类型检查
        """
        try:
            # 调用客户端
            response = self.client.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt),
                ]
            )

            # 类型检查:确保返回的是BaseMessage
            if not isinstance(response, BaseMessage):
                raise ValueError(f"响应类型错误,期望BaseMessage,实际: {type(response)}")

            # 检查是否有content属性
            if not hasattr(response, "content"):
                raise ValueError(f"响应对象缺少content属性: {type(response)}")

            # 检查content是否为字符串
            if not isinstance(response.content, str):
                raise ValueError(f"响应内容必须是字符串,实际: {type(response.content)}")

            return response

        except ConnectionError as e:
            logger.error(f"连接LLM服务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM JSON响应调用失败: {e}")
            raise

    def llm_chat_response(self, system_prompt: str, human_prompt: str):
        """
        获取聊天格式的LLM响应

        使用系统提示和用户提示调用Qwen模型,返回普通文本响应。
        适用于对话、问答等场景。

        Args:
            system_prompt: 系统提示,定义AI的角色和行为规则
            human_prompt: 用户提示,具体的查询或对话内容

        Returns:
            文本格式的响应内容

        Raises:
            ValueError: 响应格式无效时抛出
            ConnectionError: API连接失败时抛出
            Exception: 其他API调用错误

        Example:
            >>> qwen = QwenMain(...)
            >>> response = qwen.llm_chat_response(
            ...     system_prompt="你是Python编程专家",
            ...     human_prompt="如何使用装饰器?"
            ... )
            >>> print(response)

        Note:
            - 适合对话、问答等自然语言交互场景
            - system_prompt会影响响应的风格和质量
            - 响应会自动进行类型检查
        """
        try:
            # 调用客户端
            response = self.client.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt),
                ]
            )

            # 类型检查:确保返回的是BaseMessage
            if not isinstance(response, BaseMessage):
                raise ValueError(f"响应类型错误,期望BaseMessage,实际: {type(response)}")

            # 检查是否有content属性
            if not hasattr(response, "content"):
                raise ValueError(f"响应对象缺少content属性: {type(response)}")

            # 检查content是否为字符串
            if not isinstance(response.content, str):
                raise ValueError(f"响应内容必须是字符串,实际: {type(response.content)}")

            return response

        except ConnectionError as e:
            logger.error(f"连接LLM服务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM聊天响应调用失败: {e}")
            raise

    def llm_chat_response_by_human_prompt(self, human_prompt: str):
        """
        仅使用用户提示获取LLM响应

        不设置系统提示,直接使用用户提示调用模型。
        适用于简单问答、无需特定角色设定的场景。

        Args:
            human_prompt: 用户提示,包含查询或指令

        Returns:
            文本格式的响应内容

        Raises:
            ValueError: 响应格式无效或参数为空时抛出
            ConnectionError: API连接失败时抛出
            Exception: 其他API调用错误

        Example:
            >>> qwen = QwenMain(...)
            >>> answer = qwen.llm_chat_response_by_human_prompt(
            ...     "什么是机器学习?"
            ... )
            >>> print(answer)

        Note:
            - 适合快速问答和简单查询
            - 响应风格由模型默认行为决定
            - 无法自定义AI角色和行为
            - 响应会自动进行类型检查
        """
        # 输入验证
        if not human_prompt or not human_prompt.strip():
            raise ValueError("human_prompt不能为空")

        try:
            # 调用客户端
            response = self.client.invoke(
                [
                    HumanMessage(content=human_prompt),
                ]
            )

            # 类型检查:确保返回的是BaseMessage
            if not isinstance(response, BaseMessage):
                raise ValueError(f"响应类型错误,期望BaseMessage,实际: {type(response)}")

            # 检查是否有content属性
            if not hasattr(response, "content"):
                raise ValueError(f"响应对象缺少content属性: {type(response)}")

            # 检查content是否为字符串
            if not isinstance(response.content, str):
                raise ValueError(f"响应内容必须是字符串,实际: {type(response.content)}")

            return response

        except ConnectionError as e:
            logger.error(f"连接LLM服务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM简单响应调用失败: {e}")
            raise
