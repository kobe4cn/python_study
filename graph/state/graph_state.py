"""
GraphState - LangGraph工作流状态定义模块
==========================================

本模块定义了Adaptive RAG工作流中的状态类型。GraphState包含了工作流执行过程中所需的所有状态信息，
包括用户问题、生成内容、检索文档、控制流决策等。

状态字段说明:
    question: 用户的原始问题
    generation: LLM生成的答案内容
    web_search: 网络搜索决策标志
    max_retries: 答案生成的最大重试次数
    answers: 当前答案生成次数计数器
    loop_step: 工作流循环迭代计数器（自动累加）
    documents: 检索到的相关文档列表
    retriever: 向量存储检索器实例
    history_messages: 多轮对话历史记录

使用示例:
    >>> state = GraphState(
    ...     question="什么是RAG?",
    ...     max_retries=3,
    ...     answers=0,
    ...     loop_step=0,
    ...     documents=[],
    ...     retriever=vector_store.as_retriever()
    ... )

注意事项:
    - loop_step使用Annotated和operator.add实现自动累加
    - max_retries用于防止无限循环
    - retriever必须是BaseRetriever的实例

作者: AI Assistant
日期: 2025-10-05
版本: 2.0
"""

from __future__ import annotations
from typing_extensions import TypedDict
from typing import Annotated, List
import operator
from langchain_core.retrievers import BaseRetriever


class GraphState(TypedDict):
    """
    LangGraph工作流状态定义

    定义了Adaptive RAG工作流中的所有状态字段。使用TypedDict提供类型提示和IDE支持。

    Attributes:
        question (str): 用户输入的原始查询问题
            示例: "什么是大语言模型的幻觉问题?"

        generation (str): LLM生成的答案内容
            示例: "大语言模型的幻觉问题是指模型生成的内容与事实不符..."

        web_search (str): 网络搜索决策标志
            可选值: "Yes" - 需要网络搜索, "No" - 不需要网络搜索
            用途: 控制是否触发网络搜索节点

        max_retries (int): 答案生成的最大重试次数限制
            默认值: 3
            用途: 防止答案生成失败时无限循环
            示例: 如果生成的答案质量不佳，最多重试3次

        answers (int): 当前答案生成次数计数器
            初始值: 0
            用途: 跟踪已经尝试生成答案的次数
            配合max_retries使用判断是否需要停止

        loop_step (Annotated[int, operator.add]): 工作流循环迭代计数器
            初始值: 0
            特性: 使用operator.add注解实现自动累加
            用途: 跟踪整个工作流的执行步骤数

        documents (List[str]): 检索到的相关文档内容列表
            示例: ["文档1内容...", "文档2内容...", "文档3内容..."]
            用途: 存储从向量数据库或网络搜索获取的上下文文档

        retriever (BaseRetriever): 向量存储检索器实例
            类型: LangChain的BaseRetriever接口实现
            用途: 从向量数据库中检索相关文档
            示例: QdrantVectorStore.as_retriever()

        history_messages (List[str]): 多轮对话历史记录
            格式: ["用户: 问题1", "助手: 回答1", "用户: 问题2", "助手: 回答2"]
            用途: 支持多轮对话上下文

    工作流示例:
        1. 初始状态:
           {
               "question": "什么是RAG?",
               "max_retries": 3,
               "answers": 0,
               "loop_step": 0,
               "documents": [],
               "retriever": retriever_instance
           }

        2. 检索后状态:
           {
               ...,
               "loop_step": 1,
               "documents": ["RAG是检索增强生成...", "RAG包含三个步骤..."]
           }

        3. 生成后状态:
           {
               ...,
               "loop_step": 2,
               "answers": 1,
               "generation": "RAG（Retrieval-Augmented Generation）是..."
           }

    注意事项:
        - 所有字段在工作流执行过程中可能被修改
        - loop_step会在每个节点自动递增
        - documents在retrieve和web_search节点被填充
        - generation在generate节点被填充
    """

    question: str
    generation: str
    web_search: str
    max_retries: int
    answers: int
    loop_step: Annotated[int, operator.add]
    documents: List[str]
    retriever: BaseRetriever
    history_messages: List[str]
