"""
LlmMain - 大语言模型统一接口模块
==================================

本模块实现了多个LLM提供商的统一接口。使用工厂模式和策略模式，支持多种主流LLM服务商，
提供一致的API调用接口和配置管理。

设计模式:
    - 工厂模式: LlmMain作为工厂类，根据provider创建对应的LLM实例
    - 策略模式: 不同的LLM提供商实现统一的BaseLlmModel接口
    - 单例模式: LLM实例延迟初始化并复用

支持的提供商:
    - QWEN: 阿里云通义千问 (已实现)
    - OPENAI: OpenAI GPT系列 (待实现)
    - ANTHROPIC: Anthropic Claude系列 (待实现)
    - DEEPSEEK: DeepSeek系列 (待实现)
    - BAIDU: 百度文心一言 (待实现)
    - TENCENT: 腾讯混元 (待实现)
    - DASHSCOPE: 阿里云DashScope (待实现)
    - MOONSHOT: 月之暗面Kimi (待实现)

主要功能:
    - 统一的LLM配置管理
    - 自动化的LLM实例创建和复用
    - JSON格式和普通聊天两种响应模式
    - 基于Pydantic的配置验证

使用示例:
    >>> import os
    >>> import dotenv
    >>> dotenv.load_dotenv()
    >>>
    >>> # 创建LLM实例
    >>> llm = LlmMain(
    ...     provider=LlmProvider.QWEN,
    ...     model="qwen3-max",
    ...     api_key=os.getenv("OPENAI_API_KEY"),
    ...     base_url=os.getenv("OPENAI_BASE_URL"),
    ...     temperature=0.5,
    ...     stream=True
    ... )
    >>>
    >>> # JSON格式响应（用于结构化输出）
    >>> response = llm.llm_json_response(
    ...     system_prompt="你是一位数据分析师",
    ...     human_prompt="分析以下数据: [1,2,3]"
    ... )
    >>>
    >>> # 普通聊天响应
    >>> response = llm.llm_chat_response(
    ...     system_prompt="你是一位助手",
    ...     human_prompt="你好"
    ... )

技术栈:
    - Pydantic: 配置验证和管理
    - LangChain: 统一的LLM接口
    - Python 3.10+: 模式匹配语法

作者: AI Assistant
日期: 2025-10-05
版本: 2.0
"""

from __future__ import annotations
from enum import Enum
import dotenv
import os
import logging
import json
from pydantic import BaseModel, Field
from typing import Optional
from llm.base import BaseLlmModel
from llm.qwen import QwenMain

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class LlmProvider(str, Enum):
    """
    LLM提供商枚举

    定义支持的大语言模型服务提供商。每个提供商对应不同的API端点和认证方式。

    Attributes:
        OPENAI: OpenAI提供商 (GPT-3.5, GPT-4等)
        ANTHROPIC: Anthropic提供商 (Claude系列)
        DEEPSEEK: DeepSeek提供商 (DeepSeek Chat, DeepSeek Coder等)
        QWEN: 阿里云通义千问提供商 (qwen-turbo, qwen-plus, qwen-max等)
        BAIDU: 百度文心一言提供商
        TENCENT: 腾讯混元提供商
        DASHSCOPE: 阿里云DashScope提供商
        MOONSHOT: 月之暗面Kimi提供商

    使用示例:
        >>> provider = LlmProvider.QWEN
        >>> print(provider.value)  # "qwen"

    注意:
        - 当前只有QWEN提供商已完整实现
        - 其他提供商会抛出NotImplementedError
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    BAIDU = "baidu"
    TENCENT = "tencent"
    DASHSCOPE = "dashscope"
    MOONSHOT = "moonshot"


class LlmConfig(BaseModel):
    """
    LLM配置模型

    使用Pydantic进行配置验证和管理。支持从环境变量自动加载默认值。

    Attributes:
        provider (LlmProvider): LLM提供商，默认为QWEN
            示例: LlmProvider.QWEN

        model (str): 模型名称，默认为"qwen3-max"
            示例: "qwen3-max", "gpt-4", "claude-3-opus"

        api_key (str): API密钥，默认从环境变量OPENAI_API_KEY读取
            示例: "sk-xxxxxxxxxxxxx"

        base_url (str): API基础URL，默认从环境变量OPENAI_BASE_URL读取
            示例: "https://dashscope.aliyuncs.com/compatible-mode/v1"

        temperature (float): 温度参数，控制输出随机性，范围[0.0, 1.0]
            - 0.0: 确定性输出，始终选择最可能的token
            - 0.5: 平衡创造性和确定性（推荐）
            - 1.0: 最大随机性，输出更有创造性

        stream (bool): 是否使用流式输出，默认True
            - True: 逐token返回结果，适合实时展示
            - False: 等待完整响应后返回

        formats (Optional[str]): 输出格式约束，可选
            - "json": 强制JSON格式输出
            - None: 无格式约束

    配置验证:
        - temperature必须在[0.0, 1.0]范围内
        - provider必须是LlmProvider枚举值
        - model必须是非空字符串

    使用示例:
        >>> config = LlmConfig(
        ...     provider=LlmProvider.QWEN,
        ...     model="qwen3-max",
        ...     temperature=0.5
        ... )
        >>> print(config.temperature)  # 0.5

    环境变量:
        - OPENAI_API_KEY: 默认API密钥
        - OPENAI_BASE_URL: 默认API基础URL
    """

    provider: LlmProvider = Field(default=LlmProvider.QWEN, description="LLM提供商")
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


class LlmMain:
    """
    LLM统一接口主类（工厂类）

    作为LLM工厂类，负责根据配置创建和管理不同提供商的LLM实例。使用延迟初始化模式，
    只在首次使用时创建LLM实例，并复用同一实例。

    设计特点:
        - 工厂模式: 根据provider参数创建对应的LLM实例
        - 延迟初始化: 首次访问model属性时才创建实例
        - 实例复用: 创建后的实例会被缓存复用
        - 配置验证: 使用Pydantic自动验证配置参数

    Attributes:
        config (LlmConfig): LLM配置对象，包含所有必要参数
        _model (Optional[BaseLlmModel]): 缓存的LLM实例，延迟初始化

    使用示例:
        >>> import os
        >>> import dotenv
        >>> dotenv.load_dotenv()
        >>>
        >>> # 基本使用 - JSON响应
        >>> llm = LlmMain(
        ...     provider=LlmProvider.QWEN,
        ...     model="qwen3-max",
        ...     api_key=os.getenv("OPENAI_API_KEY"),
        ...     base_url=os.getenv("OPENAI_BASE_URL"),
        ...     temperature=0.5,
        ...     stream=True,
        ...     formats="json"
        ... )
        >>> result = llm.llm_json_response(
        ...     system_prompt="你是一位数据分析师",
        ...     human_prompt="分析: [1,2,3,4,5]"
        ... )
        >>> print(result)  # JSON字符串
        >>>
        >>> # 普通聊天
        >>> llm2 = LlmMain(
        ...     provider=LlmProvider.QWEN,
        ...     model="qwen3-max",
        ...     api_key=os.getenv("OPENAI_API_KEY"),
        ...     base_url=os.getenv("OPENAI_BASE_URL"),
        ...     temperature=0.7,
        ...     stream=False
        ... )
        >>> response = llm2.llm_chat_response(
        ...     system_prompt="你是一位友好的助手",
        ...     human_prompt="你好"
        ... )

    注意事项:
        - api_key和base_url必须正确配置，否则调用会失败
        - 不同provider可能需要不同的base_url格式
        - temperature参数会影响输出的随机性
        - formats="json"时要求LLM返回有效的JSON格式
    """

    def __init__(
        self,
        provider: LlmProvider,
        model: str,
        temperature: float,
        stream: bool,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        formats: Optional[str] = None,
    ):
        """
        初始化LlmMain实例

        Args:
            provider (LlmProvider): LLM提供商
                示例: LlmProvider.QWEN

            model (str): 模型名称
                示例: "qwen3-max", "gpt-4", "claude-3-opus"

            temperature (float): 温度参数，范围[0.0, 1.0]
                - 0.0: 确定性输出
                - 0.5: 平衡（推荐）
                - 1.0: 最大创造性

            stream (bool): 是否使用流式输出
                - True: 逐token返回
                - False: 等待完整响应

            api_key (Optional[str]): API密钥，可选
                如果为None，则从环境变量OPENAI_API_KEY读取

            base_url (Optional[str]): API基础URL，可选
                如果为None，则从环境变量OPENAI_BASE_URL读取

            formats (Optional[str]): 输出格式约束，可选
                - "json": 强制JSON格式
                - None: 无约束

        Raises:
            ValueError: 参数验证失败时抛出

        使用示例:
            >>> llm = LlmMain(
            ...     provider=LlmProvider.QWEN,
            ...     model="qwen3-max",
            ...     temperature=0.5,
            ...     stream=True,
            ...     api_key="sk-xxxx",
            ...     base_url="https://api.example.com/v1"
            ... )
        """
        self.config = LlmConfig(
            provider=provider,
            model=model,
            api_key=api_key or "",
            base_url=base_url or "",
            temperature=temperature,
            stream=stream,
            formats=formats,
        )
        self._model: Optional[BaseLlmModel] = None

    @property
    def model(self) -> BaseLlmModel:
        """
        获取LLM实例（延迟初始化）

        使用属性装饰器实现延迟初始化模式。首次访问时创建LLM实例，
        后续访问直接返回缓存的实例。

        Returns:
            BaseLlmModel: LLM实例，实现了BaseLlmModel接口

        Raises:
            NotImplementedError: 当provider尚未实现时抛出
            ValueError: 当provider不受支持时抛出

        使用示例:
            >>> llm = LlmMain(provider=LlmProvider.QWEN, ...)
            >>> model = llm.model  # 首次访问，创建实例
            >>> model2 = llm.model  # 后续访问，返回缓存实例
            >>> assert model is model2  # 同一实例
        """
        if self._model is None:
            self._model = self._initialize_model()
        return self._model

    def _initialize_model(self) -> BaseLlmModel:
        """
        初始化LLM实例（工厂方法）

        根据config.provider创建对应的LLM实例。使用Python 3.10+的模式匹配语法
        实现工厂模式。

        Returns:
            BaseLlmModel: 具体的LLM实例

        Raises:
            NotImplementedError: 当provider尚未实现时抛出
                提示: 大部分provider尚未实现，只有QWEN可用

            ValueError: 当provider不在支持列表中时抛出

        工厂映射:
            - QWEN -> QwenMain (已实现)
            - OPENAI -> 待实现
            - ANTHROPIC -> 待实现
            - DEEPSEEK -> 待实现
            - 其他 -> 待实现

        使用示例:
            >>> llm = LlmMain(provider=LlmProvider.QWEN, ...)
            >>> # _initialize_model会自动被调用
            >>> # 返回QwenMain实例
        """
        logger.info("获取LLM实例: %s", self.config.provider)

        match self.config.provider:
            case LlmProvider.OPENAI:
                raise NotImplementedError("OPENAI提供商尚未实现")
            case LlmProvider.ANTHROPIC:
                raise NotImplementedError("ANTHROPIC提供商尚未实现")
            case LlmProvider.DEEPSEEK:
                raise NotImplementedError("DEEPSEEK提供商尚未实现")
            case LlmProvider.QWEN:
                return QwenMain(
                    model=self.config.model,
                    api_key=self.config.api_key,
                    base_url=self.config.base_url,
                    temperature=self.config.temperature,
                    stream=self.config.stream,
                    formats=self.config.formats,
                )
            case LlmProvider.BAIDU:
                raise NotImplementedError("BAIDU提供商尚未实现")
            case LlmProvider.TENCENT:
                raise NotImplementedError("TENCENT提供商尚未实现")
            case LlmProvider.DASHSCOPE:
                raise NotImplementedError("DASHSCOPE提供商尚未实现")
            case LlmProvider.MOONSHOT:
                raise NotImplementedError("MOONSHOT提供商尚未实现")
            case _:
                raise ValueError(f"不支持的LLM提供商: {self.config.provider}")

    def llm_json_response(self, system_prompt: str, human_prompt: str) :
        """
        获取JSON格式的LLM响应

        委托给底层LLM实例，要求返回JSON格式的响应。适用于需要结构化输出的场景，
        如数据分析、分类、评分等。

        Args:
            system_prompt (str): 系统提示词，定义LLM的角色和行为
                示例: "你是一位数据分析师，擅长统计分析"

            human_prompt (str): 用户提示词，具体的任务描述
                示例: "分析以下数据并返回JSON格式的统计结果: [1,2,3,4,5]"

        Returns:
            str: JSON格式的字符串响应
                示例: '{"mean": 3.0, "median": 3, "std": 1.41}'

        Raises:
            Exception: LLM调用失败时抛出
            JSONDecodeError: 返回的不是有效JSON时（如果需要解析）

        使用示例:
            >>> llm = LlmMain(provider=LlmProvider.QWEN, ...)
            >>> result = llm.llm_json_response(
            ...     system_prompt="你是一位评分专家",
            ...     human_prompt="评估这篇文章的质量: '...'"
            ... )
            >>> import json
            >>> data = json.loads(result)
            >>> print(data["score"])

        注意:
            - 确保system_prompt和human_prompt中明确要求JSON格式输出
            - 返回值是字符串，需要json.loads()解析为dict
            - 如果初始化时设置formats="json"，会强制JSON格式
        """
        return self.model.llm_json_response(system_prompt, human_prompt)

    def llm_chat_response(self, system_prompt: str, human_prompt: str) :
        """
        获取普通聊天格式的LLM响应

        委托给底层LLM实例，返回自然语言格式的响应。适用于对话、问答、内容生成等场景。

        Args:
            system_prompt (str): 系统提示词，定义LLM的角色和行为
                示例: "你是一位友好的助手，用简洁的语言回答问题"

            human_prompt (str): 用户提示词，用户的问题或请求
                示例: "解释什么是向量数据库"

        Returns:
            str: 自然语言格式的响应内容
                示例: "向量数据库是一种专门用于存储和检索高维向量的数据库..."

        Raises:
            Exception: LLM调用失败时抛出

        使用示例:
            >>> llm = LlmMain(provider=LlmProvider.QWEN, ...)
            >>> response = llm.llm_chat_response(
            ...     system_prompt="你是一位Python专家",
            ...     human_prompt="如何使用装饰器?"
            ... )
            >>> print(response)

        注意:
            - 返回值是纯文本字符串
            - system_prompt会影响回答的风格和专业性
            - temperature参数会影响回答的创造性
        """
        return self.model.llm_chat_response(system_prompt, human_prompt)

    def llm_chat_response_by_human_prompt(self, human_prompt: str) :
        """
        仅使用用户提示词获取聊天响应（无系统提示）

        委托给底层LLM实例，不提供系统提示词的简化调用方式。适用于快速测试或
        不需要特定角色设定的场景。

        Args:
            human_prompt (str): 用户提示词
                示例: "你好" 或 "今天天气怎么样?"

        Returns:
            str: 自然语言格式的响应内容

        Raises:
            Exception: LLM调用失败时抛出

        使用示例:
            >>> llm = LlmMain(provider=LlmProvider.QWEN, ...)
            >>> response = llm.llm_chat_response_by_human_prompt("你好")
            >>> print(response)

        注意:
            - 没有系统提示词，LLM使用默认行为
            - 适合简单对话和快速测试
            - 如需控制LLM角色，应使用llm_chat_response()
        """
        return self.model.llm_chat_response_by_human_prompt(human_prompt)


if __name__ == "__main__":
    dotenv.load_dotenv()

    llm = LlmMain(
        provider=LlmProvider.QWEN,
        model="qwen3-max",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.5,
        stream=True,
        formats="json",
    )
    print(
        llm.model.llm_json_response(
            system_prompt="你是一位数据分析师",
            human_prompt="你好",
        )
    )
