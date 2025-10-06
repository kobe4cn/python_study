"""
UDF工具模块 - 用户自定义功能工具集
=====================================

本模块提供了一系列用户自定义工具(UDF),主要包括网络搜索功能。
集成了DuckDuckGo和Tavily两种搜索引擎,支持多种输出格式。

主要功能:
    - DuckDuckGo搜索: 免费的网络搜索工具
    - Tavily搜索: 专业的AI搜索工具,支持高级功能
    - 多格式输出: 支持JSON、列表、字符串、Document等
    - 实例复用: 搜索工具在初始化时创建,避免重复实例化

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
版本: 1.0.1
"""

from __future__ import annotations

import logging
import json
from typing import Literal, List, Dict, Union

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_tavily.tavily_search import TavilySearch
from langchain_core.documents import Document


logger = logging.getLogger(__name__)


class UdfTools:
    """
    用户自定义工具类

    提供各种实用工具函数,主要聚焦于网络搜索功能。支持DuckDuckGo和
    Tavily两种搜索引擎,可根据需求选择。

    搜索工具在初始化时创建并复用,避免重复实例化带来的性能开销。

    Attributes:
        _duck_search_list: DuckDuckGo列表格式搜索工具实例
        _duck_search_json: DuckDuckGo JSON格式搜索工具实例
        _tavily_tool: Tavily搜索工具实例

    Example:
        >>> tools = UdfTools()
        >>> # DuckDuckGo搜索
        >>> results = tools.duck_search("人工智能")
        >>> # Tavily搜索
        >>> result = tools.tavily_search("深度学习", top_k=3)

    Note:
        - 搜索工具实例在__init__中创建并复用
        - 支持多种输出格式
        - DuckDuckGo无需API密钥
        - Tavily需要设置TAVILY_API_KEY环境变量
    """

    def __init__(self) -> None:
        """
        初始化UDF工具类

        创建并初始化所有搜索工具实例,这些实例会被复用以提高性能。

        Example:
            >>> tools = UdfTools()
            >>> # 工具已初始化,立即可用

        Note:
            - DuckDuckGo工具会创建两个实例(list和json格式)
            - Tavily工具默认配置为返回前5个结果
        """
        # 初始化DuckDuckGo搜索工具(复用实例)
        self._duck_search_list = DuckDuckGoSearchResults(output_format="list")
        self._duck_search_json = DuckDuckGoSearchResults(output_format="json")

        # 初始化Tavily搜索工具(复用实例)
        self._tavily_tool = TavilySearch(
            max_results=5,
            include_answers=True,
            include_raw_content=True,
            include_images=True,
        )

        logger.info("UDF工具初始化完成")

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
                - 支持自然语言查询
                - 支持关键词搜索
            output_format: 输出格式,可选"json"或"list",默认"list"

        Returns:
            搜索结果摘要片段列表,每个元素是一个字符串

        Raises:
            ValueError: 不支持的输出格式时抛出
            Exception: 搜索失败时抛出

        Example:
            >>> tools = UdfTools()
            >>> # 列表格式(推荐)
            >>> results = tools.duck_search("Python最佳实践")
            >>> for snippet in results:
            ...     print(f"- {snippet}")
            >>>
            >>> # JSON格式
            >>> results = tools.duck_search("机器学习入门", output_format="json")
            >>> print(f"找到 {len(results)} 条相关结果")

        Note:
            - 结果数量由DuckDuckGo API决定,通常返回5-10条
            - 摘要可能被截断
            - 频繁请求可能被限流
            - 使用预初始化的工具实例,性能更优
        """
        try:
            if output_format == "list":
                # 使用list格式工具实例
                result = self._duck_search_list.invoke(query)
                return [res["snippet"] for res in result]
            elif output_format == "json":
                # 使用json格式工具实例
                data = self._duck_search_json.invoke(query)
                parsed_data = json.loads(data)
                return [item["snippet"] for item in parsed_data]
            else:
                raise ValueError(f"不支持的输出格式: {output_format}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise ValueError(f"无法解析搜索结果: {e}") from e
        except Exception as e:
            logger.error(f"DuckDuckGo搜索失败: {query} - {e}")
            raise

    def tavily_search(
        self,
        query: str,
        top_k: int = 5,
        output_format: Literal["string", "document"] = "document",
    ) -> Dict[str, Union[str, Document]]:
        """
        Tavily专业AI搜索

        使用Tavily搜索引擎进行专业的AI增强搜索。Tavily提供更高质量的
        搜索结果,包括答案、原始内容和图片,特别适合RAG应用。

        Args:
            query: 搜索查询字符串
                - 支持复杂查询
                - 支持专业术语
                - AI优化的查询理解
            top_k: 返回的最大结果数,默认5
                - 范围: 1-10(建议)
                - 更多结果提供更全面的信息
                - 更少结果响应更快
            output_format: 输出格式,可选"string"或"document",默认"document"

        Returns:
            包含搜索结果的字典:
                - output_format="string": {"content": str}
                - output_format="document": {"content": Document}

        Raises:
            ValueError: 不支持的输出格式时抛出
            KeyError: 环境变量TAVILY_API_KEY未设置时抛出
            Exception: Tavily API调用失败时抛出

        Example:
            >>> import dotenv
            >>> dotenv.load_dotenv()
            >>> tools = UdfTools()
            >>>
            >>> # Document格式(推荐用于RAG)
            >>> result = tools.tavily_search(
            ...     query="大语言模型的最新进展",
            ...     top_k=5,
            ...     output_format="document"
            ... )
            >>> doc = result["content"]
            >>> print(f"内容: {doc.page_content[:200]}...")
            >>> print(f"来源: {doc.metadata['source']}")
            >>>
            >>> # 字符串格式(简单使用)
            >>> result = tools.tavily_search(
            ...     query="Python 3.12新特性",
            ...     top_k=3,
            ...     output_format="string"
            ... )
            >>> print(result["content"])

        Tavily特性:
            - include_answers: 包含AI生成的答案
            - include_raw_content: 包含原始网页内容
            - include_images: 包含相关图片URL
            - 语义搜索优化
            - 高质量结果过滤

        配置要求:
            环境变量:
                TAVILY_API_KEY: Tavily API密钥

            获取API密钥:
                访问 https://tavily.com 注册并获取

        Note:
            - 确保已设置TAVILY_API_KEY环境变量
            - 注意API配额限制
            - top_k过大会增加响应时间
            - Document格式更适合与LangChain集成
            - 使用预初始化的工具实例,性能更优
        """
        try:
            # 更新工具的max_results配置
            self._tavily_tool.max_results = top_k

            # 调用Tavily搜索
            docs = self._tavily_tool.invoke({"query": query})
            # print("-" * 50, type(docs))
            # print("-" * 50, docs)
            # 提取并拼接搜索结果内容
            str_docs = "\n".join([doc["content"] for doc in docs["results"]])

            # 根据输出格式返回结果
            if output_format == "string":
                return {"content": str_docs}
            elif output_format == "document":
                from datetime import datetime

                # 收集搜索结果的URL
                urls = [result.get("url", "") for result in docs.get("results", [])]

                return {
                    "content": Document(
                        page_content=str_docs,
                        metadata={
                            "source": "tavily_search",
                            "query": query,
                            "search_timestamp": datetime.utcnow().isoformat(),
                            "num_results": len(docs.get("results", [])),
                            "urls": urls,
                            "search_engine": "tavily",
                        }
                    )
                }
            else:
                raise ValueError("不支持的输出格式: %s", output_format)

        except KeyError as e:
            logger.error("Tavily搜索结果格式错误: %s", e)
            raise ValueError(f"无法解析Tavily搜索结果: {e}") from e
        except Exception as e:
            logger.error("Tavily搜索失败: %s - %s", query, e)
            raise

    @staticmethod
    def format_docs(docs) -> str:
        """
        格式化文档
        Format documents

        Args:
            docs: 文档列表

        Returns:
            格式化后的文档字符串

        Example:
            >>> docs = [Document(page_content="文档1"), Document(page_content="文档2")]
            >>> udf_tools.format_docs(docs)
            >>> "文档1\n文档2"

        """
        # print("-" * 50, docs)
        # print("-" * 50, type(docs))
        # print("-" * 50, [doc.page_content for doc in docs])
        # print("-" * 50, "\n".join([doc.page_content for doc in docs]))
        return "\n".join([doc.page_content for doc in docs])


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    udf_tools = UdfTools()

    def duck_search_test():
        """测试DuckDuckGo搜索"""
        print("=== DuckDuckGo搜索测试 ===")
        print(udf_tools.duck_search("RWA是什么?", output_format="list"))
        print("-" * 50)
        print(udf_tools.duck_search("RWA是什么?", output_format="json"))
        print("-" * 50)

    def tavily_search_test():
        """测试Tavily搜索"""
        # print("=== Tavily搜索测试 ===")
        # print(udf_tools.tavily_search("RWA是什么?", output_format="string"))
        # print("-" * 50)
        udf_tools.tavily_search("RWA是什么?", output_format="document")
        print("-" * 50)

    # 运行测试
    # duck_search_test()
    tavily_search_test()
