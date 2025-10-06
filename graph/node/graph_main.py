"""
GraphMain - LangGraph工作流主控制器模块
========================================

本模块实现了Adaptive RAG工作流的主控制器。GraphMain负责构建、配置和编译LangGraph工作流，
定义节点之间的连接关系和条件路由逻辑。

工作流架构:
    1. 入口路由: route_question -> vectorstore/websearch
    2. 向量检索路径: retrieve -> grade_documents -> generate
    3. 网络搜索路径: websearch -> generate
    4. 答案质量评估: grade_generation_v_documents_and_question -> 重试/结束

主要功能:
    - 构建包含多个节点的状态图
    - 配置条件路由和边连接
    - 编译工作流并生成可视化图表
    - 提供流式执行接口

使用示例:
    >>> import dotenv
    >>> dotenv.load_dotenv()
    >>> graph = GraphMain()
    >>> for event in graph.stream("什么是RAG?"):
    ...     if "generation" in event:
    ...         print(event["generation"].content)

技术栈:
    - LangGraph: 状态图工作流引擎
    - Qdrant: 向量数据库
    - LangChain: 检索器接口

作者: AI Assistant
日期: 2025-10-05
版本: 2.0
"""

from __future__ import annotations
from graph.state.graph_state import GraphState
from graph.func.graph_func import (
    retrieve,
    generate,
    grade_documents,
    web_search,
    route_question,
    decide_to_generate,
    grade_generation_v_documents_and_question,
)
from langgraph.graph import StateGraph, END
from doc.vstore.vstore_main import VStoreMain, VectorStoreProvider
from langgraph.checkpoint.redis import RedisSaver
from uuid import uuid4


class GraphMain:
    """
    LangGraph工作流主控制器

    负责构建和管理Adaptive RAG工作流。该类封装了工作流的构建、配置、编译和执行逻辑。

    工作流节点:
        - retrieve: 从向量数据库检索相关文档
        - grade_documents: 评估检索文档的相关性
        - generate: 基于文档生成答案
        - websearch: 执行网络搜索获取最新信息

    工作流路由:
        1. 入口路由 (route_question):
           - vectorstore: 问题适合向量检索 -> retrieve节点
           - websearch: 问题需要最新信息 -> websearch节点

        2. 文档评估后路由 (decide_to_generate):
           - generate: 文档相关性充分 -> generate节点
           - websearch: 文档不够相关 -> websearch节点

        3. 答案质量评估路由 (grade_generation_v_documents_and_question):
           - useful: 答案质量良好 -> END
           - not supported: 答案存在幻觉 -> 重新生成
           - not useful: 答案不够有用 -> websearch
           - max retries: 达到最大重试次数 -> END

    Attributes:
        workflow (StateGraph): LangGraph状态图实例
        _graph: 编译后的可执行工作流

    使用示例:
        >>> # 基本使用
        >>> graph = GraphMain()
        >>> results = []
        >>> for event in graph.stream("什么是向量数据库?"):
        ...     if "generation" in event and event["generation"]:
        ...         results.append(event["generation"].content)
        >>> print("".join(results))

        >>> # 查看工作流可视化
        >>> # 执行后会生成 graph.png 文件展示工作流结构

    注意事项:
        - 工作流在初始化时自动编译
        - 每次执行都会创建新的向量存储连接
        - 生成的graph.png保存在当前工作目录
        - 需要正确配置环境变量（OPENAI_API_KEY等）
    """

    def __init__(self):
        """
        初始化GraphMain实例

        执行步骤:
            1. 创建StateGraph实例
            2. 添加节点和配置路由
            3. 编译工作流
            4. 生成可视化图表

        Raises:
            Exception: 工作流构建或编译失败时抛出异常
        """
        self.workflow = self._build_graph()
        self._set_graph()
        self._graph = None
        self._compile_graph()

    def _build_graph(self) -> StateGraph:
        """
        构建状态图实例

        Returns:
            StateGraph: 基于GraphState的状态图实例

        注意:
            使用GraphState作为状态类型定义
        """
        return StateGraph(GraphState)

    def _set_graph(self) -> None:
        """
        配置工作流节点和边

        添加节点:
            - retrieve: 向量检索节点
            - generate: 答案生成节点
            - grade_documents: 文档评分节点
            - websearch: 网络搜索节点

        配置路由:
            - 条件入口: route_question决定初始路径
            - 固定边: retrieve -> grade_documents, websearch -> generate
            - 条件边: grade_documents和generate的多路径路由

        工作流图结构:
                     [START]
                        |
                  route_question
                   /          \
            vectorstore      websearch
                /                 \
            retrieve             (直接)
                |                   \
          grade_documents         generate
              /        \              |
        generate    websearch   grade_generation
            \          /              |
             generate           useful/not useful/
                |               not supported/
             grade...           max retries
                |                   |
            [END]                [END]
        """
        workflow = self.workflow
        workflow.add_node("retrieve", retrieve)
        workflow.add_node("generate", generate)
        workflow.add_node("grade_documents", grade_documents)
        workflow.add_node("websearch", web_search)

        # 用户首次提问是使用网络搜索还是RAG检索
        workflow.set_conditional_entry_point(
            route_question, {"websearch": "websearch", "vectorstore": "retrieve"}
        )

        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_edge("websearch", "generate")

        workflow.add_conditional_edges(
            "grade_documents",
            decide_to_generate,
            {"websearch": "websearch", "generate": "generate"},
        )

        workflow.add_conditional_edges(
            "generate",
            grade_generation_v_documents_and_question,
            {
                "useful": END,
                "not supported": "generate",
                "max retries": END,
                "not useful": "websearch",
            },
        )

    def _compile_graph(self):
        """
        编译工作流并生成可视化图表

        执行操作:
            1. 编译StateGraph为可执行工作流
            2. 生成Mermaid格式的PNG流程图

        Returns:
            编译后的可执行工作流实例

        副作用:
            在当前目录生成 graph.png 文件

        Raises:
            Exception: 编译失败或图表生成失败时抛出异常
        """
        DB_URI = "redis://localhost:6379/10"
        conn_ctx = RedisSaver.from_conn_string(DB_URI)
        memory = conn_ctx.__enter__()
        self._graph = self.workflow.compile(checkpointer=memory)
        # 生成流程图png保存到当前目录
        self._graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        return self._graph

    def stream(self, user_inputs: str, config):
        """
        执行工作流并返回流式结果

        Args:
            user_inputs (str): 用户输入的问题
                示例: "什么是RAG?" 或 "最新的LLaMA模型有哪些?"

        Returns:
            Generator: 流式事件生成器，每个事件包含当前状态

        事件结构示例:
            {
                "question": "什么是RAG?",
                "documents": ["文档1", "文档2"],
                "generation": AIMessage对象,
                "loop_step": 2,
                ...
            }

        使用示例:
            >>> graph = GraphMain()
            >>> for event in graph.stream("什么是向量数据库?"):
            ...     # 每个event包含当前完整状态
            ...     if "generation" in event and event["generation"]:
            ...         print(event["generation"].content)

        注意事项:
            - 每次调用都会创建新的向量存储连接
            - 使用stream_mode="values"返回完整状态
            - max_retries设置为3，防止无限循环
            - 需要Qdrant服务正常运行

        Raises:
            Exception: 向量存储连接失败或工作流执行异常
        """
        VectorStore = VStoreMain(
            vector_store_provider=VectorStoreProvider.QDRANT,
            collection_name="document_store",
        )
        retriever = VectorStore.as_retriever()
        inputs = {"question": user_inputs, "max_retries": 3, "retriever": retriever}
        return self._graph.stream(inputs, stream_mode="values", config=config)

    def get_state_history(self, config):
        return self._graph.get_state_history(config)


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    graph = GraphMain()
    # graph.get_graph().draw_mermaid_png(filename="graph.png")

    inputs = "What are the models released today for llama3.2?"

    # 配置快照信息，用于记录每次执行的快照信息
    config = {"configurable": {"thread_id": uuid4()}}
    # inputs = "截止到今天llama3.2已经发布了哪些版本的模型"
    result = []
    for event in graph.stream(inputs, config):
        # print(type(event["generation"]))
        # print(event)

        if "generation" in event and event["generation"]:
            result.append(event["generation"].content)
    print(result)

    stat_history = list(graph.get_state_history(config))
    for state in stat_history:
        print(state)
