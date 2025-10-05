"""
BaseLlmModel - LLM抽象基类模块
==================================

本模块定义了所有LLM实现必须遵循的统一接口。使用抽象基类（ABC）模式，
确保所有LLM提供商的实现都遵循相同的方法签名和行为契约。

设计模式:
    - 抽象基类模式（ABC）: 定义接口契约
    - 策略模式: 不同LLM提供商作为可互换的策略
    - 模板方法模式: 定义统一的方法签名

接口方法:
    - llm_json_response: JSON格式响应接口
    - llm_chat_response: 普通聊天响应接口
    - llm_chat_response_by_human_prompt: 简化聊天响应接口

实现要求:
    所有继承BaseLlmModel的类必须实现全部抽象方法，否则无法实例化。

已知实现:
    - QwenMain: 阿里云通义千问实现（llm/qwen.py）
    - 其他提供商实现（待补充）

使用示例:
    >>> from llm.base import BaseLlmModel
    >>> from llm.qwen import QwenMain
    >>>
    >>> # QwenMain实现了BaseLlmModel接口
    >>> llm: BaseLlmModel = QwenMain(
    ...     model="qwen3-max",
    ...     api_key="sk-xxx",
    ...     base_url="https://...",
    ...     temperature=0.5,
    ...     stream=True
    ... )
    >>>
    >>> # 可以使用统一的接口方法
    >>> response = llm.llm_chat_response(
    ...     system_prompt="你是助手",
    ...     human_prompt="你好"
    ... )

扩展指南:
    要实现新的LLM提供商，需要：
    1. 继承BaseLlmModel
    2. 实现所有@abstractmethod装饰的方法
    3. 在llm_main.py的工厂方法中注册新提供商

    示例：
    >>> class NewProviderLlm(BaseLlmModel):
    ...     def llm_json_response(self, system_prompt: str, human_prompt: str):
    ...         # 实现JSON响应逻辑
    ...         pass
    ...
    ...     def llm_chat_response(self, system_prompt: str, human_prompt: str):
    ...         # 实现聊天响应逻辑
    ...         pass
    ...
    ...     def llm_chat_response_by_human_prompt(self, human_prompt: str):
    ...         # 实现简化响应逻辑
    ...         pass

作者: AI Assistant
日期: 2025-10-05
版本: 2.0
"""

from abc import ABC, abstractmethod


class BaseLlmModel(ABC):
    """
    LLM模型抽象基类

    定义所有LLM实现必须遵循的统一接口。使用Python的ABC（抽象基类）机制
    确保接口一致性和类型安全。

    设计理念:
        - 所有LLM提供商实现相同的接口
        - 支持依赖倒置原则（DIP）
        - 方便测试和mock
        - 支持多态和策略替换

    抽象方法:
        子类必须实现以下三个方法：
        1. llm_json_response: 返回JSON格式的结构化响应
        2. llm_chat_response: 返回自然语言格式的聊天响应
        3. llm_chat_response_by_human_prompt: 简化版聊天响应（无系统提示）

    使用示例:
        >>> from llm.base import BaseLlmModel
        >>> from llm.qwen import QwenMain
        >>>
        >>> # 使用抽象类型声明，支持任何实现
        >>> def process_with_llm(llm: BaseLlmModel, prompt: str) -> str:
        ...     return llm.llm_chat_response("你是助手", prompt)
        >>>
        >>> # 可以传入任何BaseLlmModel的实现
        >>> qwen = QwenMain(...)
        >>> result = process_with_llm(qwen, "你好")

    实现要求:
        - 子类必须实现所有@abstractmethod方法
        - 方法签名必须完全匹配
        - 返回类型应该一致（通常为str）
        - 异常处理应在实现类中完成

    多态示例:
        >>> # 可以轻松切换不同的LLM提供商
        >>> llms: List[BaseLlmModel] = [
        ...     QwenMain(...),
        ...     # OpenAILlm(...),  # 未来实现
        ...     # ClaudeLlm(...),  # 未来实现
        ... ]
        >>> for llm in llms:
        ...     response = llm.llm_chat_response("你是助手", "你好")

    注意事项:
        - 不能直接实例化BaseLlmModel
        - 子类必须实现所有抽象方法才能实例化
        - 建议在子类中添加具体的类型提示和文档
    """

    @abstractmethod
    def llm_json_response(self, system_prompt: str, human_prompt: str) :
        """
        获取JSON格式的LLM响应（抽象方法）

        子类必须实现此方法以返回JSON格式的结构化输出。适用于需要解析和
        处理结构化数据的场景，如评分、分类、数据分析等。

        Args:
            system_prompt (str): 系统提示词，定义LLM的角色和行为
                示例: "你是一位数据分析师，返回JSON格式的分析结果"

            human_prompt (str): 用户提示词，具体的任务描述
                示例: "分析以下数据: [1, 2, 3, 4, 5]"

        Returns:
            str: JSON格式的字符串响应
                示例: '{"mean": 3.0, "median": 3, "count": 5}'

        Raises:
            Exception: LLM调用失败或网络错误时抛出
            JSONDecodeError: 如果返回的不是有效JSON（实现类应避免）

        实现要求:
            - 必须返回有效的JSON字符串
            - 应处理LLM API调用的异常
            - 建议添加重试机制
            - 应记录日志便于调试

        实现示例（伪代码）:
            >>> def llm_json_response(self, system_prompt: str, human_prompt: str) -> str:
            ...     # 1. 构建消息
            ...     messages = [
            ...         {"role": "system", "content": system_prompt},
            ...         {"role": "user", "content": human_prompt}
            ...     ]
            ...     # 2. 调用LLM API
            ...     response = self.client.chat(messages, format="json")
            ...     # 3. 提取并返回JSON字符串
            ...     return response.content

        使用示例:
            >>> llm = QwenMain(...)  # 某个实现类
            >>> result = llm.llm_json_response(
            ...     system_prompt="你是评分专家，返回JSON格式",
            ...     human_prompt="评估这段代码的质量"
            ... )
            >>> import json
            >>> data = json.loads(result)
            >>> print(data["score"])
        """
        pass

    @abstractmethod
    def llm_chat_response(self, system_prompt: str, human_prompt: str) :
        """
        获取普通聊天格式的LLM响应（抽象方法）

        子类必须实现此方法以返回自然语言格式的响应。适用于对话、问答、
        内容生成等不需要结构化输出的场景。

        Args:
            system_prompt (str): 系统提示词，定义LLM的角色和行为
                示例: "你是一位友好的Python编程助手"

            human_prompt (str): 用户提示词，用户的问题或请求
                示例: "如何使用Python读取CSV文件?"

        Returns:
            str: 自然语言格式的响应内容
                示例: "使用pandas库的read_csv()方法可以轻松读取CSV文件..."

        Raises:
            Exception: LLM调用失败或网络错误时抛出

        实现要求:
            - 返回纯文本字符串
            - 应处理LLM API调用的异常
            - 可选择是否流式返回
            - 应记录日志便于调试

        实现示例（伪代码）:
            >>> def llm_chat_response(self, system_prompt: str, human_prompt: str) -> str:
            ...     # 1. 构建消息
            ...     messages = [
            ...         {"role": "system", "content": system_prompt},
            ...         {"role": "user", "content": human_prompt}
            ...     ]
            ...     # 2. 调用LLM API
            ...     if self.stream:
            ...         # 流式响应
            ...         chunks = []
            ...         for chunk in self.client.stream(messages):
            ...             chunks.append(chunk.content)
            ...         return "".join(chunks)
            ...     else:
            ...         # 非流式响应
            ...         response = self.client.chat(messages)
            ...         return response.content

        使用示例:
            >>> llm = QwenMain(...)  # 某个实现类
            >>> response = llm.llm_chat_response(
            ...     system_prompt="你是Python专家",
            ...     human_prompt="解释装饰器的作用"
            ... )
            >>> print(response)
        """
        pass

    @abstractmethod
    def llm_chat_response_by_human_prompt(self, human_prompt: str) :
        """
        仅使用用户提示词获取聊天响应（抽象方法）

        子类必须实现此方法以提供简化的调用方式。不需要系统提示词，
        适用于快速测试或简单对话场景。

        Args:
            human_prompt (str): 用户提示词
                示例: "你好" 或 "解释什么是机器学习"

        Returns:
            str: 自然语言格式的响应内容

        Raises:
            Exception: LLM调用失败或网络错误时抛出

        实现要求:
            - 内部可以使用默认的系统提示词或不使用系统提示
            - 返回纯文本字符串
            - 应处理异常情况
            - 建议复用llm_chat_response的实现逻辑

        实现示例（伪代码）:
            >>> def llm_chat_response_by_human_prompt(self, human_prompt: str) -> str:
            ...     # 方式1: 使用默认系统提示
            ...     return self.llm_chat_response(
            ...         system_prompt="你是一位友好的助手",
            ...         human_prompt=human_prompt
            ...     )
            ...
            ...     # 方式2: 不使用系统提示
            ...     messages = [{"role": "user", "content": human_prompt}]
            ...     response = self.client.chat(messages)
            ...     return response.content

        使用示例:
            >>> llm = QwenMain(...)  # 某个实现类
            >>> response = llm.llm_chat_response_by_human_prompt("你好")
            >>> print(response)

        与llm_chat_response的区别:
            - llm_chat_response: 需要system_prompt和human_prompt两个参数
            - llm_chat_response_by_human_prompt: 只需要human_prompt一个参数
            - 前者更灵活，后者更简洁
        """
        pass
