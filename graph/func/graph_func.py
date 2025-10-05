"""
Graph函数模块 - LangGraph节点和路由函数
======================================

本模块提供LangGraph工作流中使用的所有节点函数和路由函数。
实现了自适应RAG(检索增强生成)的核心逻辑。

主要功能:
    - 节点函数(Nodes): retrieve, generate, grade_documents, web_search
    - 路由函数(Routes): route_question, decide_to_generate, grade_generation

工作流程:
    1. route_question: 决定使用向量检索还是网络搜索
    2. retrieve: 从向量存储检索相关文档
    3. grade_documents: 评估检索文档的相关性
    4. decide_to_generate: 决定是否需要网络搜索补充
    5. web_search: 执行网络搜索获取额外信息
    6. generate: 基于文档生成答案
    7. grade_generation: 评估生成答案的质量

典型用法:
    >>> from graph.func.graph_func import retrieve, generate
    >>> state = {"question": "什么是AI?", "retriever": retriever}
    >>> result = retrieve(state)
    >>> answer = generate(result)

作者: Kevin
创建日期: 2025
版本: 1.1.0
"""

from __future__ import annotations
import logging
import json
import os
from typing import Dict, Any, Optional

from tools.udf_tools import UdfTools
from graph.prompt.prompt import (
    RAG_PROMPT,
    DOC_GRADER_PROMPT,
    DOC_GRADER_INSTRUCTIONS,
    ROUTER_INSTRUCTIONS,
    HALLUCINATION_GRADER_PROMPT,
    HALLUCINATION_GRADER_INSTRUCTIONS,
    ANSWER_GRADER_PROMPT,
    ANSWER_GRADER_INSTRUCTIONS,
)
from llm.llm_main import LlmMain, LlmProvider

logger = logging.getLogger(__name__)


# ==================== 辅助函数 ====================


def _create_llm_instance(formats: Optional[str] = None) -> LlmMain:
    """
    创建LLM实例(内部辅助函数)

    统一创建LLM实例的方法,确保所有必要参数都正确传递。

    Args:
        formats: 响应格式,"json"或None

    Returns:
        配置好的LlmMain实例

    Raises:
        ValueError: 环境变量未设置时抛出
    """
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise ValueError("环境变量OPENAI_API_KEY未设置")
    if not base_url:
        raise ValueError("环境变量OPENAI_BASE_URL未设置")

    return LlmMain(
        provider=LlmProvider.QWEN,
        model="qwen3-max",
        api_key=api_key,
        base_url=base_url,
        temperature=0.5,
        stream=True,
        formats=formats,
    )


# ==================== 节点函数 (Nodes) ====================


def retrieve(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    从向量存储中检索文档

    根据用户问题,从向量存储中检索相关文档。

    Args:
        state: 图状态字典,必须包含:
            - question (str): 用户问题
            - retriever (BaseRetriever): 检索器实例

    Returns:
        包含检索到的文档的状态更新字典:
            - documents (List[Document]): 检索到的文档列表

    Raises:
        KeyError: 状态缺少必要字段时抛出
        Exception: 检索失败时抛出

    Example:
        >>> state = {"question": "什么是AI?", "retriever": retriever}
        >>> result = retrieve(state)
        >>> print(len(result["documents"]))

    Note:
        - 检索结果数量由retriever的top_k配置决定
        - 文档按相关性排序
    """
    try:
        question = state["question"]
        retriever = state["retriever"]

        logger.info(f"检索文档 for question: {question}")

        # 执行检索
        documents = retriever.invoke(question)

        logger.info(f"检索到 {len(documents)} 个文档")

        return {"documents": documents}

    except KeyError as e:
        logger.error(f"状态缺少必要字段: {e}")
        raise ValueError(f"retrieve函数需要的字段缺失: {e}") from e
    except Exception as e:
        logger.error(f"文档检索失败: {e}")
        raise


def generate(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成答案

    基于检索到的文档和用户问题,使用LLM生成答案。

    Args:
        state: 图状态字典,必须包含:
            - question (str): 用户问题
            - documents (List[Document]): 相关文档列表
            - loop_step (int, optional): 当前循环步数,默认0

    Returns:
        包含生成答案的状态更新字典:
            - generation (str): LLM生成的答案
            - loop_step (int): 更新后的循环步数

    Raises:
        KeyError: 状态缺少必要字段时抛出
        Exception: LLM调用失败时抛出

    Example:
        >>> state = {
        ...     "question": "什么是AI?",
        ...     "documents": [doc1, doc2],
        ...     "loop_step": 0
        ... }
        >>> result = generate(state)
        >>> print(result["generation"])

    Note:
        - 使用RAG_PROMPT模板格式化提示
        - 文档会被格式化为文本上下文
        - loop_step用于跟踪重试次数
    """
    try:
        question = state["question"]
        documents = state["documents"]
        loop_step = state.get("loop_step", 0)

        logger.info(f"生成答案 for question: {question}, loop_step: {loop_step}")

        # 格式化文档
        formatted_documents = UdfTools.format_docs(documents)

        # 构建RAG提示
        rag_format_prompt = RAG_PROMPT.format(
            context=formatted_documents, question=question
        )

        # 创建LLM实例并生成答案
        llm = _create_llm_instance()
        answer = llm.llm_chat_response_by_human_prompt(rag_format_prompt)

        logger.info(f"答案生成成功,长度: {len(answer.content)}")

        return {"generation": answer, "loop_step": loop_step + 1}

    except KeyError as e:
        logger.error(f"状态缺少必要字段: {e}")
        raise ValueError(f"generate函数需要的字段缺失: {e}") from e
    except Exception as e:
        logger.error(f"答案生成失败: {e}")
        raise


def grade_documents(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    评估检索到的文档相关性

    使用LLM评估每个检索到的文档是否与问题相关,过滤掉不相关的文档。

    Args:
        state: 图状态字典,必须包含:
            - question (str): 用户问题
            - documents (List[Document]): 待评估的文档列表

    Returns:
        包含过滤后文档的状态更新字典:
            - documents (List[Document]): 相关文档列表
            - web_search (str): "yes"或"no",指示是否需要网络搜索

    Raises:
        KeyError: 状态缺少必要字段时抛出
        json.JSONDecodeError: LLM返回的JSON格式错误时抛出
        Exception: 其他错误

    Example:
        >>> state = {"question": "什么是AI?", "documents": [doc1, doc2, doc3]}
        >>> result = grade_documents(state)
        >>> print(len(result["documents"]))  # 过滤后的文档数
        >>> print(result["web_search"])  # "yes" 或 "no"

    Note:
        - 使用DOC_GRADER_PROMPT评估每个文档
        - 如果所有文档都不相关,web_search设为"yes"
        - binary_score为"yes"表示文档相关
    """
    try:
        question = state["question"]
        documents = state["documents"]

        logger.info(
            f"评估文档相关性 for question: {question}, 文档数: {len(documents)}"
        )

        filtered_documents = []
        web_search = "no"

        # 创建JSON格式的LLM实例
        llm_json = _create_llm_instance(formats="json")

        for idx, doc in enumerate(documents):
            try:
                # 构建评估提示
                grade_prompt = DOC_GRADER_PROMPT.format(
                    question=question, document=doc.page_content
                )

                # 调用LLM评估
                result_str = llm_json.llm_json_response(
                    DOC_GRADER_INSTRUCTIONS, grade_prompt
                )

                # 解析JSON响应
                result_dict = json.loads(result_str)
                binary_score = result_dict.get("binary_score", "no")

                if binary_score.lower() == "yes":
                    filtered_documents.append(doc)
                    logger.debug(f"文档 {idx + 1} 相关")
                else:
                    logger.info(f"文档 {idx + 1} 不相关,已过滤")

            except json.JSONDecodeError as e:
                logger.error(f"文档 {idx + 1} 评估JSON解析失败: {e}")
                # 保守策略:解析失败时保留文档
                filtered_documents.append(doc)
            except Exception as e:
                logger.error(f"文档 {idx + 1} 评估失败: {e}")
                # 保守策略:评估失败时保留文档
                filtered_documents.append(doc)

        # 如果没有相关文档,需要网络搜索
        if len(filtered_documents) == 0:
            web_search = "yes"
            logger.info(f"没有找到相关文档,需要网络搜索")
        else:
            logger.info(f"找到 {len(filtered_documents)} 个相关文档")

        return {"documents": filtered_documents, "web_search": web_search}

    except KeyError as e:
        logger.error(f"状态缺少必要字段: {e}")
        raise ValueError(f"grade_documents函数需要的字段缺失: {e}") from e
    except Exception as e:
        logger.error(f"文档评估失败: {e}")
        raise


def web_search(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行网络搜索

    使用Tavily搜索引擎获取问题的相关网络信息。

    Args:
        state: 图状态字典,必须包含:
            - question (str): 用户问题
            - documents (List[Document], optional): 现有文档列表,默认空列表

    Returns:
        包含搜索结果的状态更新字典:
            - documents (List[Document]): 更新后的文档列表(添加了搜索结果)

    Raises:
        KeyError: 状态缺少question字段时抛出
        Exception: 搜索失败时抛出

    Example:
        >>> state = {"question": "最新的AI进展", "documents": []}
        >>> result = web_search(state)
        >>> print(len(result["documents"]))  # 添加了搜索结果

    Note:
        - 使用Tavily搜索,返回top 5结果
        - 搜索结果以Document格式添加到现有文档列表
        - 需要设置TAVILY_API_KEY环境变量
    """
    try:
        question = state["question"]
        documents = state.get("documents", [])

        logger.info(f"执行网络搜索 for question: {question}")

        # 执行Tavily搜索
        tools = UdfTools()
        search_result = tools.tavily_search(question, top_k=5, output_format="document")

        # 添加搜索结果到文档列表
        documents.append(search_result["content"])

        logger.info(f"网络搜索完成,添加了搜索结果文档")

        return {"documents": documents}

    except KeyError as e:
        logger.error(f"状态缺少必要字段: {e}")
        raise ValueError(f"web_search函数需要question字段: {e}") from e
    except Exception as e:
        logger.error(f"网络搜索失败: {e}")
        raise


# ==================== 路由函数 (Routes) ====================


def route_question(state: Dict[str, Any]) -> str:
    """
    路由用户问题到向量存储或网络搜索

    决定用户问题应该使用向量存储检索还是直接网络搜索。

    Args:
        state: 图状态字典,必须包含:
            - question (str): 用户问题

    Returns:
        路由决策:
            - "websearch": 使用网络搜索
            - "vectorstore": 使用向量存储检索

    Raises:
        KeyError: 状态缺少question字段时抛出
        json.JSONDecodeError: LLM返回的JSON格式错误时抛出
        Exception: 其他错误

    Example:
        >>> state = {"question": "今天的新闻"}
        >>> route = route_question(state)
        >>> print(route)  # "websearch"
        >>>
        >>> state = {"question": "什么是Transformer架构?"}
        >>> route = route_question(state)
        >>> print(route)  # "vectorstore"

    Note:
        - 向量存储包含AI、提示工程等主题的文档
        - 当前事件、新闻等问题会路由到网络搜索
        - 使用ROUTER_INSTRUCTIONS判断
    """
    try:
        question = state["question"]

        logger.info(f"路由问题: {question}")

        # 创建JSON格式的LLM实例
        llm_json = _create_llm_instance(formats="json")

        # 调用LLM进行路由决策
        result_str = llm_json.llm_json_response(ROUTER_INSTRUCTIONS, question)
        # print("-" * 50, result_str)
        # 解析JSON响应
        result_dict = json.loads(result_str.content)
        datasource = result_dict.get("datasource", "vectorstore")

        if datasource.lower() == "websearch":
            logger.info(f"路由到网络搜索 for question: {question}")
            return "websearch"
        else:
            logger.info(f"路由到向量存储 for question: {question}")
            return "vectorstore"

    except KeyError as e:
        logger.error(f"状态缺少question字段: {e}")
        raise ValueError(f"route_question函数需要question字段: {e}") from e
    except json.JSONDecodeError as e:
        logger.error(f"路由决策JSON解析失败: {e},默认使用向量存储")
        return "vectorstore"  # 默认使用向量存储
    except Exception as e:
        logger.error(f"路由决策失败: {e},默认使用向量存储")
        return "vectorstore"  # 默认使用向量存储


def decide_to_generate(state: Dict[str, Any]) -> str:
    """
    决定是否可以生成答案或需要网络搜索

    基于文档评估结果,决定下一步行动。

    Args:
        state: 图状态字典,必须包含:
            - question (str): 用户问题
            - web_search (str): "yes"或"no"

    Returns:
        决策结果:
            - "websearch": 需要网络搜索
            - "generate": 可以生成答案

    Raises:
        KeyError: 状态缺少必要字段时抛出

    Example:
        >>> state = {"question": "什么是AI?", "web_search": "no"}
        >>> decision = decide_to_generate(state)
        >>> print(decision)  # "generate"
        >>>
        >>> state = {"question": "什么是AI?", "web_search": "yes"}
        >>> decision = decide_to_generate(state)
        >>> print(decision)  # "websearch"

    Note:
        - 如果web_search为"yes",表示文档不足,需要网络搜索
        - 如果web_search为"no",表示文档充足,可以生成答案
    """
    try:
        question = state["question"]
        web_search = state["web_search"]

        logger.info(
            f"决定下一步行动 for question: {question}, web_search: {web_search}"
        )

        if web_search.lower() == "yes":
            logger.info(f"需要网络搜索补充信息")
            return "websearch"
        else:
            logger.info(f"可以直接生成答案")
            return "generate"

    except KeyError as e:
        logger.error(f"状态缺少必要字段: {e}")
        raise ValueError(f"decide_to_generate函数需要的字段缺失: {e}") from e


def grade_generation_v_documents_and_question(state: Dict[str, Any]) -> str:
    """
    评估生成答案的质量

    检查生成的答案是否:
    1. 基于提供的文档(没有幻觉)
    2. 能够回答用户问题

    Args:
        state: 图状态字典,必须包含:
            - question (str): 用户问题
            - generation (str): LLM生成的答案
            - documents (List[Document]): 参考文档列表
            - max_retries (int): 最大重试次数
            - loop_step (int): 当前循环步数

    Returns:
        评估结果:
            - "useful": 答案有效,可以结束
            - "not supported": 答案有幻觉,需要重新生成
            - "not useful": 答案无法回答问题,需要网络搜索
            - "max retries": 达到最大重试次数,结束

    Raises:
        KeyError: 状态缺少必要字段时抛出
        json.JSONDecodeError: LLM返回的JSON格式错误时抛出
        Exception: 其他错误

    Example:
        >>> state = {
        ...     "question": "什么是AI?",
        ...     "generation": "AI是人工智能...",
        ...     "documents": [doc1, doc2],
        ...     "max_retries": 3,
        ...     "loop_step": 1
        ... }
        >>> result = grade_generation_v_documents_and_question(state)
        >>> print(result)  # "useful" 或 "not useful" 等

    Note:
        - 首先检查幻觉(答案是否基于文档)
        - 然后检查答案质量(是否回答问题)
        - 根据loop_step判断是否已达最大重试次数
    """
    try:
        question = state["question"]
        generation = state["generation"]
        documents = state["documents"]
        max_retries = state["max_retries"]
        loop_step = state.get("loop_step", 0)

        logger.info(
            f"评估答案质量 for question: {question}, loop_step: {loop_step}/{max_retries}"
        )

        # 创建JSON格式的LLM实例
        llm_json = _create_llm_instance(formats="json")

        # 第一步:检查幻觉
        hallucination_prompt = HALLUCINATION_GRADER_PROMPT.format(
            documents=UdfTools.format_docs(documents), generation=generation
        )

        try:
            hallucination_result_str = llm_json.llm_json_response(
                HALLUCINATION_GRADER_INSTRUCTIONS, hallucination_prompt
            )
            hallucination_dict = json.loads(hallucination_result_str.content)
            hallucination_grade = hallucination_dict.get("binary_score", "no")

        except json.JSONDecodeError as e:
            logger.error(f"幻觉检查JSON解析失败: {e},假设有幻觉")
            hallucination_grade = "no"

        # 如果没有幻觉,检查答案质量
        if hallucination_grade.lower() == "yes":
            logger.info("答案没有幻觉,检查答案质量")

            # 第二步:检查答案质量
            answer_prompt = ANSWER_GRADER_PROMPT.format(
                question=question, generation=generation
            )

            try:
                answer_result_str = llm_json.llm_json_response(
                    ANSWER_GRADER_INSTRUCTIONS, answer_prompt
                )
                answer_dict = json.loads(answer_result_str.content)
                answer_grade = answer_dict.get("binary_score", "no")

            except json.JSONDecodeError as e:
                logger.error(f"答案质量检查JSON解析失败: {e},假设答案无效")
                answer_grade = "no"

            if answer_grade.lower() == "yes":
                logger.info("答案有效")
                return "useful"
            elif loop_step <= max_retries:
                logger.info("答案无效,需要网络搜索补充")
                return "not useful"
            else:
                logger.info("答案无效且达到最大重试次数")
                return "max retries"

        # 有幻觉的情况
        elif loop_step <= max_retries:
            logger.info("答案有幻觉,需要重新生成")
            return "not supported"
        else:
            logger.info("答案有幻觉且达到最大重试次数")
            return "max retries"

    except KeyError as e:
        logger.error(f"状态缺少必要字段: {e}")
        raise ValueError(f"grade_generation函数需要的字段缺失: {e}") from e
    except Exception as e:
        logger.error(f"答案评估失败: {e}")
        # 默认返回max retries以避免无限循环
        return "max retries"
