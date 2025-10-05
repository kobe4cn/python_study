"""
Prompt Templates - Adaptive RAG工作流提示词模板模块
====================================================

本模块包含Adaptive RAG工作流中所有节点使用的提示词模板。这些模板定义了LLM在不同阶段的
角色、任务和输出格式要求。

工作流提示词概览:
    1. RAG生成提示词: 基于上下文生成答案
    2. 文档相关性评估提示词: 评估检索文档是否相关
    3. 路由决策提示词: 决定使用向量检索还是网络搜索
    4. 幻觉检测提示词: 检测生成内容是否基于事实
    5. 答案质量评估提示词: 评估答案是否解决问题

模板使用方法:
    所有模板都是Python字符串，使用.format()方法填充占位符。

    示例:
    >>> prompt = RAG_PROMPT.format(
    ...     context="向量数据库用于存储高维向量...",
    ...     question="什么是向量数据库?"
    ... )

设计理念:
    - 所有评估类提示词都要求返回JSON格式
    - 提示词强调简洁性和准确性
    - 包含明确的评分标准和示例
    - 使用中文提示以适配中文问答场景

注意事项:
    - 修改提示词可能影响工作流的准确性
    - JSON格式要求确保了结果的可解析性
    - 提示词中的占位符必须与代码中的参数名一致

作者: AI Assistant
日期: 2025-10-05
版本: 2.0
"""

# ================================
# 1. RAG答案生成提示词
# ================================

RAG_PROMPT = """你是一名用于问答任务的助手。

以下是回答问题时需要使用的上下文：

{context}

请认真思考以上上下文。

现在，请审阅用户的问题：

{question}

请仅基于上述上下文回答问题。

回答时最多使用三句话，并保持简洁。

答案："""

"""
RAG_PROMPT - RAG答案生成模板

用途:
    在generate节点中使用，要求LLM基于检索到的上下文文档生成答案。

占位符:
    - {context}: 检索到的文档内容，通常是多个文档的拼接
    - {question}: 用户的原始问题

使用示例:
    >>> from tools.udf_tools import UdfTools
    >>> context = UdfTools.format_docs(documents)
    >>> prompt = RAG_PROMPT.format(context=context, question="什么是RAG?")
    >>> answer = llm.llm_chat_response("你是助手", prompt)

特点:
    - 强调仅基于上下文回答，减少幻觉
    - 要求简洁（最多三句话）
    - 明确的结构化指导

注意:
    - context应该是格式化后的文档文本
    - 如果context为空或不相关，答案质量会下降
"""


# ================================
# 2. 文档相关性评估提示词
# ================================

DOC_GRADER_INSTRUCTIONS = """你是一名评估员，负责判断检索到的文档与用户问题的相关性。

如果文档包含与问题相关的关键词或语义含义，请将其判定为相关。"""

"""
DOC_GRADER_INSTRUCTIONS - 文档评分系统提示词

用途:
    在grade_documents节点中作为system_prompt使用，定义文档评估员的角色。

角色定义:
    - 评估员角色
    - 判断文档与问题的相关性
    - 基于关键词或语义相似度

评估标准:
    - 包含相关关键词 -> 相关
    - 语义含义相关 -> 相关

使用示例:
    >>> result = llm.llm_json_response(
    ...     system_prompt=DOC_GRADER_INSTRUCTIONS,
    ...     human_prompt=DOC_GRADER_PROMPT.format(document=doc, question=q)
    ... )
"""


DOC_GRADER_PROMPT = """以下是检索到的文档：\n\n {document} \n\n 以下是用户问题：\n\n {question}。

请认真且客观地评估该文档是否至少包含与问题相关的一些信息。

返回一个 JSON，包含单一键 binary_score，其值为 'yes' 或 'no'，用于表示该文档是否至少包含与问题相关的一些信息。"""

"""
DOC_GRADER_PROMPT - 文档评分任务提示词

用途:
    在grade_documents节点中作为human_prompt使用，提供具体的评分任务。

占位符:
    - {document}: 单个检索到的文档内容
    - {question}: 用户的原始问题

返回格式:
    JSON对象，示例: {"binary_score": "yes"} 或 {"binary_score": "no"}

使用示例:
    >>> for doc in documents:
    ...     prompt = DOC_GRADER_PROMPT.format(
    ...         document=doc.page_content,
    ...         question=state["question"]
    ...     )
    ...     result = llm.llm_json_response(DOC_GRADER_INSTRUCTIONS, prompt)
    ...     score_dict = json.loads(result)
    ...     if score_dict["binary_score"] == "yes":
    ...         filtered_docs.append(doc)

评分逻辑:
    - "yes": 文档包含相关信息，保留
    - "no": 文档不相关，过滤掉

注意:
    - 必须返回有效的JSON格式
    - binary_score的值只能是"yes"或"no"
"""


# ================================
# 3. 问题路由决策提示词
# ================================

ROUTER_INSTRUCTIONS = """你是一名专家，负责将用户问题路由到向量库或网页搜索。

向量库包含与智能体、提示工程和对抗攻击相关的文档。

对于这些主题的问题，请使用向量库。对于其他所有问题，尤其是与当前事件相关的问题，请使用网页搜索。

返回一个 JSON，包含单一键 datasource，其值为 'websearch' 或 'vectorstore'，具体取决于问题。"""

"""
ROUTER_INSTRUCTIONS - 问题路由系统提示词

用途:
    在route_question节点中使用，决定使用向量检索还是网络搜索。

路由逻辑:
    - 向量库主题（智能体、提示工程、对抗攻击）-> vectorstore
    - 当前事件或其他主题 -> websearch

返回格式:
    JSON对象，示例: {"datasource": "vectorstore"} 或 {"datasource": "websearch"}

使用示例:
    >>> question = "最新的LLaMA 3.2模型有哪些?"
    >>> result = llm.llm_json_response(
    ...     system_prompt=ROUTER_INSTRUCTIONS,
    ...     human_prompt=question
    ... )
    >>> route_dict = json.loads(result)
    >>> datasource = route_dict["datasource"]  # "websearch"

决策影响:
    - vectorstore: 进入retrieve节点
    - websearch: 进入web_search节点

注意:
    - 向量库的主题范围可以根据实际数据修改此提示词
    - 当前事件通常需要网络搜索获取最新信息
"""


# ================================
# 4. 幻觉检测提示词
# ================================

HALLUCINATION_GRADER_INSTRUCTIONS = """
你是一名老师，负责为一次测验评分。

你将会得到【事实】（FACTS）和【学生答案】（STUDENT ANSWER）。

请按照以下评分标准执行：

(1) 确保【学生答案】以【事实】为依据。
(2) 确保【学生答案】不包含超出【事实】范围的"幻觉"信息。

评分说明：

评分为 yes 表示学生答案满足所有标准。这是最高（最佳）评分。
评分为 no 表示学生答案未满足所有标准。这是你能给出的最低评分。

请以逐步推理的方式解释你的理由，以确保你的推理与结论正确。

避免在一开始就直接给出正确答案。
"""

"""
HALLUCINATION_GRADER_INSTRUCTIONS - 幻觉检测系统提示词

用途:
    在grade_generation_v_documents_and_question节点中使用，检测LLM生成的答案是否包含幻觉。

角色定义:
    - 老师角色
    - 评分测验答案
    - 确保答案基于事实

评分标准:
    1. 答案必须基于事实
    2. 答案不能包含幻觉（事实之外的信息）

评分结果:
    - yes: 答案完全基于事实，无幻觉
    - no: 答案包含幻觉或不基于事实

使用示例:
    >>> result = llm.llm_json_response(
    ...     system_prompt=HALLUCINATION_GRADER_INSTRUCTIONS,
    ...     human_prompt=HALLUCINATION_GRADER_PROMPT.format(
    ...         documents=context,
    ...         generation=answer
    ...     )
    ... )
"""


HALLUCINATION_GRADER_PROMPT = """事实: \n\n {documents} \n\n 学生回答: {generation}.

请返回一个 JSON，包含两个键：
- binary_score: 值为 'yes' 或 'no'，用于表示学生回答是否基于上述事实；
- explanation: 提供对该评分的解释说明。"""

"""
HALLUCINATION_GRADER_PROMPT - 幻觉检测任务提示词

用途:
    在grade_generation_v_documents_and_question节点中使用，提供具体的幻觉检测任务。

占位符:
    - {documents}: 检索到的事实文档（上下文）
    - {generation}: LLM生成的答案

返回格式:
    JSON对象，示例:
    {
        "binary_score": "yes",
        "explanation": "答案完全基于提供的事实，没有额外信息"
    }

使用示例:
    >>> context = format_docs(state["documents"])
    >>> answer = state["generation"]
    >>> prompt = HALLUCINATION_GRADER_PROMPT.format(
    ...     documents=context,
    ...     generation=answer
    ... )
    >>> result = llm.llm_json_response(
    ...     HALLUCINATION_GRADER_INSTRUCTIONS,
    ...     prompt
    ... )
    >>> result_dict = json.loads(result)
    >>> if result_dict["binary_score"] == "no":
    ...     # 存在幻觉，需要重新生成
    ...     return "not supported"

检测逻辑:
    - "yes": 无幻觉，答案可靠
    - "no": 有幻觉，需要重新生成

工作流影响:
    - "yes": 继续答案质量评估
    - "no": 返回generate节点重新生成
"""


# ================================
# 5. 答案质量评估提示词
# ================================

ANSWER_GRADER_INSTRUCTIONS = """你是一名老师，负责为一次测验评分。

你将会得到【问题】（QUESTION）和【学生答案】（STUDENT ANSWER）。

请按照以下评分标准执行：

(1) 【学生答案】能够帮助回答【问题】。

评分说明：

评分为 yes 表示学生答案满足所有标准。这是最高（最佳）评分。
即使答案包含问题未明确要求的额外信息，只要满足标准，也可以评为 yes。
评分为 no 表示学生答案未满足所有标准。这是你能给出的最低评分。

请以逐步推理的方式解释你的理由，以确保你的推理与结论正确。
避免在一开始就直接给出正确答案。"""

"""
ANSWER_GRADER_INSTRUCTIONS - 答案质量评估系统提示词

用途:
    在grade_generation_v_documents_and_question节点中使用，评估答案是否解决了用户问题。

角色定义:
    - 老师角色
    - 评分学生答案
    - 判断答案是否有用

评分标准:
    1. 答案能够帮助回答问题

宽容性:
    - 允许答案包含额外信息
    - 只要能回答问题即可评为yes

评分结果:
    - yes: 答案有用，解决了问题
    - no: 答案无用，未解决问题

使用示例:
    >>> result = llm.llm_json_response(
    ...     system_prompt=ANSWER_GRADER_INSTRUCTIONS,
    ...     human_prompt=ANSWER_GRADER_PROMPT.format(
    ...         question=user_question,
    ...         generation=answer
    ...     )
    ... )
"""


ANSWER_GRADER_PROMPT = """问题: \n\n {question} \n\n 学生回答: {generation}.

请返回一个 JSON，包含两个键：
- binary_score: 值为 'yes' 或 'no'，用于表示学生回答是否符合要求；
- explanation: 提供该评分的解释说明。"""

"""
ANSWER_GRADER_PROMPT - 答案质量评估任务提示词

用途:
    在grade_generation_v_documents_and_question节点中使用，提供具体的答案评估任务。

占位符:
    - {question}: 用户的原始问题
    - {generation}: LLM生成的答案

返回格式:
    JSON对象，示例:
    {
        "binary_score": "yes",
        "explanation": "答案准确回答了用户的问题，提供了足够的信息"
    }

使用示例:
    >>> question = state["question"]
    >>> answer = state["generation"]
    >>> prompt = ANSWER_GRADER_PROMPT.format(
    ...     question=question,
    ...     generation=answer
    ... )
    >>> result = llm.llm_json_response(
    ...     ANSWER_GRADER_INSTRUCTIONS,
    ...     prompt
    ... )
    >>> result_dict = json.loads(result)
    >>> if result_dict["binary_score"] == "no":
    ...     # 答案质量不佳，需要网络搜索
    ...     return "not useful"

评估逻辑:
    - "yes": 答案有用，工作流结束
    - "no": 答案无用，触发网络搜索

工作流影响:
    - "yes": 返回END，结束工作流
    - "no": 返回websearch节点获取更多信息

完整评估流程:
    1. 幻觉检测（HALLUCINATION_GRADER）
       - "no": 重新生成答案
       - "yes": 继续
    2. 答案质量评估（ANSWER_GRADER）
       - "no": 网络搜索补充信息
       - "yes": 工作流结束，返回答案
"""
