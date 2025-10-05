# API 文档补充方案

> 本文档提供了为 `llm/` 和 `tools/` 目录下所有代码补充完整文档字符串的方案

---

## 📋 文档补充清单

### llm/llm_main.py

需要补充的文档:
- [x] 模块级文档字符串
- [x] LlmProvider 枚举文档
- [x] LlmConfig 类文档
- [x] BaseLlmModel 抽象基类文档
- [x] LlmMain 类及所有方法文档

### llm/qwen.py

需要补充的文档:
- [x] 模块级文档字符串
- [x] QwenConfig 类文档
- [x] QwenMain 类及所有方法文档

### tools/udf_tools.py

需要补充的文档:
- [x] 模块级文档字符串
- [x] UdfTools 类及所有方法文档

---

## 📝 文档字符串标准

### 标准格式 (Google Style)

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """
    简短的一行描述

    详细描述(可选,多行)
    提供更多上下文信息

    Args:
        param1: 参数1的描述
        param2: 参数2的描述,默认值0

    Returns:
        返回值的描述

    Raises:
        ValueError: 什么情况下抛出
        TypeError: 什么情况下抛出

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True

    Note:
        额外的注意事项
    """
    pass
```

---

## 🔧 实施方案

### 方案A: 直接修改现有文件

为每个文件添加完整的文档字符串。

**优点**:
- 文档与代码在一起
- IDE直接可用
- 符合Python最佳实践

**缺点**:
- 需要修改现有代码
- 可能影响git历史

### 方案B: 创建独立文档文件

在 `docs/` 目录下创建API文档。

**优点**:
- 不修改现有代码
- 文档可以更详细
- 易于版本控制

**缺点**:
- 文档与代码分离
- 需要手动同步更新

---

## 📄 推荐的完整文档字符串

### 1. llm/llm_main.py

#### 模块级文档

```python
"""
LLM主模块 - 统一的大语言模型访问接口
=======================================

本模块提供了对多个LLM提供商的统一访问接口,通过抽象基类和工厂模式
实现了不同LLM提供商的可互换使用。

主要组件:
    - LlmProvider: LLM提供商枚举
    - LlmConfig: LLM配置模型(基于Pydantic)
    - BaseLlmModel: LLM抽象基类,定义接口规范
    - LlmMain: LLM工厂类,统一访问入口

支持的提供商:
    - QWEN: 通义千问 (已实现)
    - OPENAI: OpenAI (待实现)
    - ANTHROPIC: Anthropic (待实现)
    - DEEPSEEK: DeepSeek (待实现)
    - BAIDU: 百度文心 (待实现)
    - TENCENT: 腾讯混元 (待实现)
    - DASHSCOPE: 阿里云灵积 (待实现)
    - MOONSHOT: 月之暗面 (待实现)

设计模式:
    - 工厂模式: 根据配置创建不同的LLM实例
    - 策略模式: 不同LLM提供商可互换使用
    - 懒加载: 延迟初始化模型直到首次使用

典型用法:
    >>> from llm.llm_main import LlmMain, LlmProvider
    >>> import os
    >>>
    >>> # 创建LLM实例
    >>> llm = LlmMain(
    ...     provider=LlmProvider.QWEN,
    ...     model="qwen3-max",
    ...     api_key=os.getenv("OPENAI_API_KEY"),
    ...     base_url=os.getenv("OPENAI_BASE_URL"),
    ...     temperature=0.7,
    ...     stream=True
    ... )
    >>>
    >>> # 使用聊天接口
    >>> response = llm.llm_chat_response(
    ...     system_prompt="你是一个AI助手",
    ...     human_prompt="你好"
    ... )
    >>> print(response)

环境变量:
    OPENAI_API_KEY: API密钥(必需)
    OPENAI_BASE_URL: API基础URL(可选)

依赖:
    - langchain_community: LangChain社区组件
    - pydantic: 数据验证和配置管理
    - python-dotenv: 环境变量加载

作者: Kevin
创建日期: 2025
版本: 1.0.0
许可证: MIT
"""
```

#### LlmProvider 枚举

```python
class LlmProvider(str, Enum):
    """
    LLM提供商枚举

    定义所有支持的大语言模型提供商标识符。每个提供商对应一个字符串值,
    可用于配置、路由和模型初始化。

    属性:
        OPENAI: OpenAI提供商,值为"openai"
        ANTHROPIC: Anthropic提供商,值为"anthropic"
        DEEPSEEK: DeepSeek提供商,值为"deepseek"
        QWEN: 通义千问提供商,值为"qwen"
        BAIDU: 百度文心提供商,值为"baidu"
        TENCENT: 腾讯混元提供商,值为"tencent"
        DASHSCOPE: 阿里云灵积提供商,值为"dashscope"
        MOONSHOT: 月之暗面提供商,值为"moonshot"

    Example:
        >>> # 使用枚举
        >>> provider = LlmProvider.QWEN
        >>> print(provider.value)
        'qwen'
        >>>
        >>> # 从字符串创建
        >>> provider = LlmProvider("qwen")
        >>>
        >>> # 遍历所有提供商
        >>> for p in LlmProvider:
        ...     print(f"{p.name}: {p.value}")

    Note:
        - 继承自str,可直接用于字符串比较
        - 提供了类型安全的提供商标识
    """
```

#### LlmConfig 类

```python
class LlmConfig(BaseModel):
    """
    LLM配置模型

    使用Pydantic BaseModel定义LLM的配置参数,提供自动验证和类型检查。
    所有参数都有合理的默认值,支持从环境变量读取敏感信息。

    Attributes:
        provider (LlmProvider): LLM提供商,默认QWEN
        model (str): 模型名称,默认"qwen3-max"
        api_key (str): API密钥,默认从环境变量OPENAI_API_KEY读取
        base_url (str): API基础URL,默认从环境变量OPENAI_BASE_URL读取
        temperature (float): 采样温度,范围0.0-1.0,默认0.5
            - 0.0-0.3: 确定性输出,适合事实性任务
            - 0.4-0.6: 平衡输出,适合一般对话
            - 0.7-1.0: 创造性输出,适合创意写作
        stream (bool): 是否启用流式响应,默认True
        formats (Optional[str]): 响应格式(如"json"),默认None

    Example:
        >>> # 使用默认配置
        >>> config = LlmConfig()
        >>>
        >>> # 自定义配置
        >>> config = LlmConfig(
        ...     provider=LlmProvider.QWEN,
        ...     model="qwen-turbo",
        ...     temperature=0.7,
        ...     stream=False
        ... )
        >>>
        >>> # 导出配置
        >>> print(config.model_dump_json(indent=2))

    Raises:
        ValidationError: 当配置参数不符合验证规则时

    Note:
        - temperature必须在0.0到1.0之间
        - api_key和base_url会自动从环境变量读取
        - 使用Pydantic的Field进行详细的字段定义
    """
```

#### BaseLlmModel 抽象基类

```python
class BaseLlmModel(ABC):
    """
    LLM模型抽象基类

    定义所有LLM模型实现必须遵循的接口规范。所有具体的LLM提供商实现
    都应继承此类并实现所有抽象方法,确保接口的一致性和可互换性。

    抽象方法:
        llm_json_response: 返回JSON格式的响应
        llm_chat_response: 返回聊天格式的响应
        llm_chat_response_by_human_prompt: 仅使用用户提示的聊天响应

    设计模式:
        - 策略模式: 定义统一接口,允许不同实现可互换使用
        - 模板方法模式: 定义算法骨架,具体步骤由子类实现

    Example:
        >>> from abc import ABC, abstractmethod
        >>>
        >>> class MyCustomLLM(BaseLlmModel):
        ...     def llm_json_response(self, system_prompt: str, human_prompt: str) -> str:
        ...         # 实现JSON响应
        ...         return '{"response": "..."}'
        ...
        ...     def llm_chat_response(self, system_prompt: str, human_prompt: str) -> str:
        ...         # 实现聊天响应
        ...         return "响应内容"
        ...
        ...     def llm_chat_response_by_human_prompt(self, human_prompt: str) -> str:
        ...         # 实现简单问答
        ...         return "响应内容"

    Note:
        - 子类必须实现所有抽象方法
        - 建议添加自定义异常处理
        - 建议实现超时和重试机制
    """

    @abstractmethod
    def llm_json_response(self, system_prompt: str, human_prompt: str) -> str:
        """
        生成JSON格式的LLM响应

        使用系统提示和用户提示调用LLM,返回JSON格式的结构化响应。

        Args:
            system_prompt: 系统提示,定义AI的角色、行为规则和输出格式要求
            human_prompt: 用户提示,包含具体的查询内容或指令

        Returns:
            JSON格式的响应字符串,可直接使用json.loads()解析

        Raises:
            NotImplementedError: 子类未实现此方法时抛出
            ValueError: 输入参数无效或为空时抛出
            ConnectionError: 网络连接失败时抛出
            TimeoutError: 请求超时时抛出

        Example:
            >>> response = model.llm_json_response(
            ...     system_prompt="你是数据分析专家,以JSON格式返回",
            ...     human_prompt="分析销售数据"
            ... )
            >>> import json
            >>> data = json.loads(response)

        Note:
            - 建议在system_prompt中明确指定JSON结构
            - 响应可能需要额外的JSON验证
        """
        pass

    @abstractmethod
    def llm_chat_response(self, system_prompt: str, human_prompt: str) -> str:
        """
        生成聊天格式的LLM响应

        使用系统提示和用户提示调用LLM,返回普通文本格式的对话响应。

        Args:
            system_prompt: 系统提示,定义AI的角色、性格和回答风格
            human_prompt: 用户提示,包含具体的查询、对话内容或指令

        Returns:
            文本格式的响应内容

        Raises:
            NotImplementedError: 子类未实现此方法时抛出
            ValueError: 输入参数无效或为空时抛出
            ConnectionError: 网络连接失败时抛出
            TimeoutError: 请求超时时抛出

        Example:
            >>> response = model.llm_chat_response(
            ...     system_prompt="你是一个友好的Python导师",
            ...     human_prompt="什么是装饰器?"
            ... )
            >>> print(response)

        Note:
            - 适合对话、问答等自然语言交互场景
            - system_prompt会影响响应的风格和质量
        """
        pass

    @abstractmethod
    def llm_chat_response_by_human_prompt(self, human_prompt: str) -> str:
        """
        仅使用用户提示生成LLM响应

        不使用系统提示,直接根据用户提示生成响应。适用于不需要特定
        角色设定的简单问答场景。

        Args:
            human_prompt: 用户提示,包含查询内容或指令

        Returns:
            文本格式的响应内容

        Raises:
            NotImplementedError: 子类未实现此方法时抛出
            ValueError: 输入参数无效或为空时抛出
            ConnectionError: 网络连接失败时抛出
            TimeoutError: 请求超时时抛出

        Example:
            >>> response = model.llm_chat_response_by_human_prompt(
            ...     "Python中的列表和元组有什么区别?"
            ... )
            >>> print(response)

        Note:
            - 适合快速问答和简单查询
            - 响应风格由模型的默认行为决定
            - 无法自定义AI角色和行为
        """
        pass
```

#### LlmMain 类

```python
class LlmMain:
    """
    LLM主类 - 统一的LLM访问入口

    提供对多个LLM提供商的统一访问接口。使用工厂模式根据配置动态创建
    相应的LLM实例,支持懒加载以优化资源使用。

    Attributes:
        config (LlmConfig): LLM配置对象,包含所有初始化参数
        _model (Optional[BaseLlmModel]): 内部LLM模型实例,懒加载

    设计模式:
        - 工厂模式: 根据provider参数创建不同的LLM实例
        - 懒加载: 延迟初始化模型直到首次访问
        - 代理模式: 代理底层LLM模型的方法调用

    Example:
        >>> import os
        >>> from llm.llm_main import LlmMain, LlmProvider
        >>>
        >>> # 创建LLM实例
        >>> llm = LlmMain(
        ...     provider=LlmProvider.QWEN,
        ...     model="qwen3-max",
        ...     api_key=os.getenv("OPENAI_API_KEY"),
        ...     base_url=os.getenv("OPENAI_BASE_URL"),
        ...     temperature=0.7,
        ...     stream=True
        ... )
        >>>
        >>> # JSON响应
        >>> json_result = llm.llm_json_response(
        ...     system_prompt="你是数据分析助手",
        ...     human_prompt="分析用户行为"
        ... )
        >>>
        >>> # 普通聊天
        >>> chat_result = llm.llm_chat_response(
        ...     system_prompt="你是AI助手",
        ...     human_prompt="你好"
        ... )
        >>>
        >>> # 简单问答
        >>> answer = llm.llm_chat_response_by_human_prompt("什么是AI?")

    Note:
        - 模型实例在首次访问时才会初始化
        - 确保环境变量中已设置必要的API密钥
        - 部分提供商可能尚未实现,会抛出NotImplementedError
    """

    def __init__(
        self,
        provider: LlmProvider,
        model: str,
        api_key: str,
        base_url: str,
        temperature: float,
        stream: bool,
        formats: Optional[str] = None,
    ):
        """
        初始化LLM主类

        创建LLM配置但不立即初始化模型实例,采用懒加载策略优化性能。

        Args:
            provider: LLM提供商枚举值,决定使用哪个LLM服务
            model: 模型名称,如"qwen3-max"、"gpt-4"等
            api_key: API密钥,用于身份验证
            base_url: API基础URL,某些提供商需要自定义端点
            temperature: 采样温度,范围0.0-1.0,控制输出的随机性
            stream: 是否启用流式响应
            formats: 响应格式,如"json",默认None表示普通文本

        Raises:
            ValidationError: 参数验证失败时抛出

        Example:
            >>> llm = LlmMain(
            ...     provider=LlmProvider.QWEN,
            ...     model="qwen-turbo",
            ...     api_key="your-api-key",
            ...     base_url="https://api.example.com",
            ...     temperature=0.5,
            ...     stream=True,
            ...     formats="json"
            ... )

        Note:
            - 模型实例在首次访问model属性时才会创建
            - temperature越高输出越随机,越低越确定
            - stream=True适合长文本生成,可逐步显示结果
        """
        pass

    @property
    def model(self) -> BaseLlmModel:
        """
        获取LLM模型实例(懒加载)

        首次访问时初始化模型,后续访问返回已缓存的实例。这种懒加载策略
        避免了不必要的资源消耗和初始化开销。

        Returns:
            LLM模型实例,类型为BaseLlmModel

        Raises:
            ValueError: 不支持的提供商时抛出
            NotImplementedError: 提供商未实现时抛出
            RuntimeError: 模型初始化失败时抛出

        Example:
            >>> llm = LlmMain(...)
            >>> # 首次访问会触发初始化
            >>> model = llm.model
            >>> # 后续访问返回缓存的实例
            >>> same_model = llm.model
            >>> assert model is same_model

        Note:
            - 这是一个property,使用时不需要加括号
            - 初始化失败会抛出异常,需要捕获处理
        """
        pass

    def _initialize_model(self) -> BaseLlmModel:
        """
        初始化LLM模型实例(内部方法)

        根据配置的provider类型,使用工厂模式创建相应的LLM实例。
        此方法由model属性在首次访问时自动调用,不应直接调用。

        Returns:
            初始化后的LLM模型实例

        Raises:
            ValueError: provider类型无效时抛出
            NotImplementedError: provider尚未实现时抛出
            RuntimeError: 模型初始化失败时抛出

        支持的提供商:
            - LlmProvider.QWEN: 返回QwenMain实例
            - 其他提供商: 抛出NotImplementedError

        Note:
            - 这是一个内部方法,以下划线开头
            - 通常不应直接调用,请使用model属性
            - 新增提供商需要在此方法中添加case分支
        """
        pass

    def llm_json_response(self, system_prompt: str, human_prompt: str) -> str:
        """
        获取JSON格式的LLM响应

        代理底层模型的JSON响应方法,提供统一的接口。适用于需要
        结构化数据的场景,如数据分析、信息提取等。

        Args:
            system_prompt: 系统提示,应明确指示返回JSON格式和结构
            human_prompt: 用户提示,具体的查询内容

        Returns:
            JSON格式的响应字符串

        Raises:
            ValueError: 参数无效时抛出
            ConnectionError: API连接失败时抛出
            JSONDecodeError: 响应不是有效JSON时可能抛出

        Example:
            >>> llm = LlmMain(provider=LlmProvider.QWEN, ...)
            >>> response = llm.llm_json_response(
            ...     system_prompt='''你是数据分析助手,以JSON格式返回:
            ...         {"summary": "摘要", "confidence": 0.95}''',
            ...     human_prompt="分析销售趋势"
            ... )
            >>> import json
            >>> data = json.loads(response)

        Note:
            - 需要在初始化时设置formats="json"以确保输出格式
            - 建议在system_prompt中明确定义JSON结构
        """
        pass

    def llm_chat_response(self, system_prompt: str, human_prompt: str) -> str:
        """
        获取聊天格式的LLM响应

        代理底层模型的聊天响应方法,返回普通文本格式。适用于对话、
        问答、内容生成等场景。

        Args:
            system_prompt: 系统提示,定义AI的角色、性格和回答风格
            human_prompt: 用户提示,具体的查询或对话内容

        Returns:
            文本格式的响应内容

        Raises:
            ValueError: 参数无效时抛出
            ConnectionError: API连接失败时抛出

        Example:
            >>> llm = LlmMain(provider=LlmProvider.QWEN, ...)
            >>> response = llm.llm_chat_response(
            ...     system_prompt="你是Python导师",
            ...     human_prompt="解释什么是装饰器"
            ... )
            >>> print(response)

        Note:
            - system_prompt会显著影响响应的风格和质量
            - 适合多轮对话场景
        """
        pass

    def llm_chat_response_by_human_prompt(self, human_prompt: str) -> str:
        """
        仅使用用户提示获取LLM响应

        不设置系统提示,直接使用用户提示获取响应。适用于不需要特定
        角色设定的简单问答场景。

        Args:
            human_prompt: 用户提示,包含查询或指令

        Returns:
            文本格式的响应内容

        Raises:
            ValueError: 参数无效时抛出
            ConnectionError: API连接失败时抛出

        Example:
            >>> llm = LlmMain(provider=LlmProvider.QWEN, ...)
            >>> answer = llm.llm_chat_response_by_human_prompt(
            ...     "Python中列表和元组的区别?"
            ... )
            >>> print(answer)

        Note:
            - 适合快速问答和简单查询
            - 无法自定义AI的角色和行为
            - 响应风格由模型默认行为决定
        """
        pass
```

---

### 2. llm/qwen.py

#### 模块级文档

```python
"""
Qwen (通义千问) LLM实现模块
================================

本模块提供通义千问大语言模型的具体实现,基于LangChain的ChatTongyi客户端。
实现了BaseLlmModel接口,支持JSON和普通文本两种响应格式。

主要特性:
    - 支持通义千问全系列模型(qwen3-max, qwen-turbo等)
    - 支持JSON格式和普通文本格式响应
    - 基于LangChain的ChatTongyi客户端
    - 灵活的配置管理和初始化策略
    - 完善的错误处理和日志记录

支持的模型:
    - qwen3-max: 通义千问3.0旗舰版,能力最强
    - qwen-turbo: 快速响应版本
    - qwen-plus: 增强版本
    - 其他通义千问API支持的模型

配置要求:
    环境变量:
        OPENAI_API_KEY: API密钥(必需)
        OPENAI_BASE_URL: API基础URL(可选)

    获取API密钥:
        访问 https://dashscope.console.aliyun.com/

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
    >>> print(response)

依赖:
    - langchain_community: ChatTongyi客户端
    - langchain_core: 消息类型定义
    - pydantic: 配置验证
    - python-dotenv: 环境变量管理

作者: Kevin
创建日期: 2025
版本: 1.0.0
"""
```

#### QwenConfig 类

```python
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

    Note:
        - temperature必须在0.0到1.0之间
        - API密钥会自动从环境变量读取
    """
```

#### QwenMain 类

```python
class QwenMain:
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
    """
```

---

### 3. tools/udf_tools.py

#### 模块级文档

```python
"""
UDF工具模块 - 用户自定义功能工具集
=====================================

本模块提供了一系列用户自定义工具(UDF),主要包括网络搜索功能。
集成了DuckDuckGo和Tavily两种搜索引擎,支持多种输出格式。

主要功能:
    - DuckDuckGo搜索: 免费的网络搜索工具
    - Tavily搜索: 专业的AI搜索工具,支持高级功能
    - 多格式输出: 支持JSON、列表、字符串、Document等
    - 灵活配置: 可控制搜索结果数量和格式

工具列表:
    - duck_search: DuckDuckGo搜索,支持json和list格式
    - tavily_search: Tavily搜索,支持string和document格式

典型用法:
    >>> from tools.udf_tools import UdfTools
    >>> import dotenv
    >>>
    >>> dotenv.load_dotenv()
    >>> tools = UdfTools()
    >>>
    >>> # DuckDuckGo搜索
    >>> results = tools.duck_search("Python教程")
    >>> for snippet in results:
    ...     print(snippet)
    >>>
    >>> # Tavily搜索
    >>> result = tools.tavily_search("机器学习", top_k=5)
    >>> print(result["content"])

配置要求:
    环境变量:
        TAVILY_API_KEY: Tavily搜索需要(可选)

    获取API密钥:
        访问 https://tavily.com

依赖:
    - langchain_community: DuckDuckGo搜索工具
    - langchain_tavily: Tavily搜索工具
    - langchain_core: Document类型定义

使用场景:
    - RAG系统的网络搜索增强
    - 实时信息检索
    - 知识库补充
    - 研究辅助

作者: Kevin
创建日期: 2025
版本: 1.0.0
"""
```

#### UdfTools 类及方法

```python
class UdfTools:
    """
    用户自定义工具类

    提供各种实用工具函数,主要聚焦于网络搜索功能。支持DuckDuckGo和
    Tavily两种搜索引擎,可根据需求选择。

    Example:
        >>> tools = UdfTools()
        >>> # DuckDuckGo搜索
        >>> results = tools.duck_search("人工智能")
        >>> # Tavily搜索
        >>> result = tools.tavily_search("深度学习", top_k=3)

    Note:
        - 无状态设计,每次调用独立执行
        - 支持多种输出格式
    """

    def duck_search(
        self,
        query: str,
        output_format: Literal["json", "list"] = "list",
    ) -> List[str]:
        """
        DuckDuckGo网络搜索

        使用DuckDuckGo搜索引擎进行网络搜索,返回搜索结果的摘要片段。
        DuckDuckGo是免费的搜索引擎,无需API密钥。

        Args:
            query: 搜索查询字符串,支持中英文
            output_format: 输出格式,可选"json"或"list",默认"list"

        Returns:
            搜索结果摘要片段列表

        Raises:
            ValueError: 不支持的输出格式时抛出
            Exception: 搜索失败时抛出

        Example:
            >>> tools = UdfTools()
            >>> results = tools.duck_search("Python最佳实践")
            >>> for snippet in results:
            ...     print(snippet)

        Note:
            - 结果数量由DuckDuckGo API决定
            - 频繁请求可能被限流
        """
        pass

    def tavily_search(
        self,
        query: str,
        top_k: int = 5,
        output_format: Literal["string", "document"] = "document",
    ) -> Dict[str, Union[str, Document]]:
        """
        Tavily专业AI搜索

        使用Tavily搜索引擎进行专业的AI增强搜索。提供更高质量的搜索结果,
        特别适合RAG应用。

        Args:
            query: 搜索查询字符串
            top_k: 返回的最大结果数,默认5
            output_format: 输出格式,"string"或"document",默认"document"

        Returns:
            包含搜索结果的字典
            - output_format="string": {"content": str}
            - output_format="document": {"content": Document}

        Raises:
            ValueError: 不支持的输出格式时抛出
            KeyError: 环境变量TAVILY_API_KEY未设置时抛出

        Example:
            >>> tools = UdfTools()
            >>> result = tools.tavily_search("大语言模型", top_k=3)
            >>> doc = result["content"]
            >>> print(doc.page_content)

        Note:
            - 需要设置TAVILY_API_KEY环境变量
            - Document格式更适合与LangChain集成
        """
        pass
```

---

## 📊 文档补充进度

- [x] llm/llm_main.py - 100%
- [x] llm/qwen.py - 100%
- [x] tools/udf_tools.py - 100%

---

## ✅ 下一步行动

1. **审查文档**: 检查所有文档字符串是否准确
2. **实施修改**: 将文档字符串添加到实际代码中
3. **生成API文档**: 使用Sphinx或pdoc生成HTML文档
4. **更新README**: 添加API文档链接

---

**文档维护者**: API Documentation Team
**最后更新**: 2025-10-05
