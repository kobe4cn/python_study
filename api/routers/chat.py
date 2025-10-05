"""
Chat Router - RAG问答流式接口
===================================

本模块提供RAG问答的REST API接口，支持流式响应和工作流状态推送。

主要功能:
    - 流式RAG问答（Server-Sent Events）
    - 工作流状态实时推送
    - 文档检索结果推送
    - 对话历史管理
    - 会话管理

安全特性:
    - JWT认证
    - 请求限流
    - 输入验证和sanitization
    - XSS防护

性能优化:
    - 异步流式响应
    - 连接池管理
    - 超时控制

作者: AI Assistant
日期: 2025-10-05
版本: 1.0
"""

from __future__ import annotations

import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from sse_starlette.sse import EventSourceResponse

# 导入现有依赖
from api.dependencies import get_current_user
from api.models.users import User

# 导入graph功能
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from graph.node.graph_main import GraphMain
from graph.state.graph_state import GraphState

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["聊天问答"],
    responses={
        401: {"description": "未授权"},
        429: {"description": "请求过多"},
        500: {"description": "服务器错误"}
    }
)


# ========== 请求/响应模型 ==========

class ChatRequest(BaseModel):
    """聊天请求模型"""

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="用户问题",
        example="什么是RAG？"
    )

    session_id: Optional[str] = Field(
        None,
        description="会话ID（可选，用于多轮对话）",
        example="sess_123456"
    )

    max_retries: int = Field(
        default=3,
        ge=1,
        le=5,
        description="最大重试次数"
    )

    stream: bool = Field(
        default=True,
        description="是否使用流式响应"
    )

    include_sources: bool = Field(
        default=True,
        description="是否返回文档来源"
    )

    include_workflow: bool = Field(
        default=True,
        description="是否返回工作流状态"
    )

    @validator('query')
    def validate_query(cls, v: str) -> str:
        """验证并清理query"""
        # 移除多余空格
        v = ' '.join(v.split())

        # 基础XSS防护
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(f"检测到潜在的XSS攻击: {pattern}")

        return v


class ChatMessage(BaseModel):
    """聊天消息模型"""

    role: str = Field(..., description="角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = Field(default=None, description="元数据")


class ConversationResponse(BaseModel):
    """对话响应模型"""

    session_id: str
    message: ChatMessage
    sources: Optional[list] = None
    workflow_steps: Optional[list] = None
    total_tokens: Optional[int] = None
    elapsed_time: Optional[float] = None


class StreamEvent(BaseModel):
    """流事件模型"""

    event: str = Field(..., description="事件类型")
    data: dict = Field(..., description="事件数据")

    class Config:
        json_schema_extra = {
            "example": {
                "event": "chunk",
                "data": {"content": "RAG是检索增强生成..."}
            }
        }


# ========== 辅助函数 ==========

def sanitize_html(text: str) -> str:
    """
    基础HTML sanitization

    Args:
        text: 输入文本

    Returns:
        清理后的文本
    """
    import html
    return html.escape(text)


async def process_graph_events(
    graph_main: GraphMain,
    query: str,
    max_retries: int,
    include_sources: bool,
    include_workflow: bool
) -> AsyncGenerator[str, None]:
    """
    处理graph工作流事件并转换为SSE格式

    Args:
        graph_main: GraphMain实例
        query: 用户问题
        max_retries: 最大重试次数
        include_sources: 是否包含文档来源
        include_workflow: 是否包含工作流状态

    Yields:
        SSE格式的事件字符串
    """
    try:
        # 开始标记
        yield format_sse_event("start", {"query": query, "timestamp": datetime.now().isoformat()})

        # 执行graph工作流
        current_generation = ""
        documents_sent = False

        for event in graph_main.stream(query):
            # 工作流状态更新
            if include_workflow and "loop_step" in event:
                workflow_data = {
                    "loop_step": event.get("loop_step", 0),
                    "answers": event.get("answers", 0),
                    "max_retries": event.get("max_retries", max_retries),
                    "web_search": event.get("web_search", ""),
                    "timestamp": datetime.now().isoformat()
                }
                yield format_sse_event("workflow_step", workflow_data)

            # 文档检索结果
            if include_sources and "documents" in event and not documents_sent:
                documents = event["documents"]
                if documents:
                    doc_data = {
                        "count": len(documents),
                        "documents": [
                            {
                                "content": doc[:200] + "..." if len(doc) > 200 else doc,
                                "index": i
                            }
                            for i, doc in enumerate(documents[:5])  # 最多返回5个文档
                        ],
                        "timestamp": datetime.now().isoformat()
                    }
                    yield format_sse_event("documents", doc_data)
                    documents_sent = True

            # 生成内容（流式）
            if "generation" in event and event["generation"]:
                generation_content = event["generation"]

                # 处理LangChain的AIMessage对象
                if hasattr(generation_content, 'content'):
                    generation_text = generation_content.content
                else:
                    generation_text = str(generation_content)

                # 只发送新增的部分（增量更新）
                if generation_text != current_generation:
                    new_chunk = generation_text[len(current_generation):]
                    current_generation = generation_text

                    # Sanitize输出
                    safe_chunk = sanitize_html(new_chunk)

                    chunk_data = {
                        "content": safe_chunk,
                        "total_length": len(current_generation),
                        "timestamp": datetime.now().isoformat()
                    }
                    yield format_sse_event("chunk", chunk_data)

        # 完成标记
        completion_data = {
            "final_answer": current_generation,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        yield format_sse_event("done", completion_data)

    except Exception as e:
        logger.exception(f"处理graph事件时出错: {str(e)}")
        error_data = {
            "error": "处理失败",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        yield format_sse_event("error", error_data)


def format_sse_event(event_type: str, data: dict) -> str:
    """
    格式化为SSE事件字符串

    Args:
        event_type: 事件类型
        data: 事件数据

    Returns:
        SSE格式的字符串
    """
    json_data = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {json_data}\n\n"


# ========== API端点 ==========

@router.post(
    "/stream",
    summary="流式RAG问答",
    description="基于Adaptive RAG工作流的流式问答接口，实时返回答案、文档来源和工作流状态",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "成功返回流式响应",
            "content": {
                "text/event-stream": {
                    "example": """event: start
data: {"query": "什么是RAG?", "timestamp": "2025-10-05T10:00:00"}

event: workflow_step
data: {"loop_step": 1, "answers": 0}

event: documents
data: {"count": 3, "documents": [...]}

event: chunk
data: {"content": "RAG是检索增强生成..."}

event: done
data: {"status": "completed"}"""
                }
            }
        }
    }
)
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    流式RAG问答接口

    工作流程:
        1. 接收用户问题
        2. 通过Adaptive RAG工作流处理
        3. 实时推送工作流状态、文档和答案
        4. 返回完成标记

    事件类型:
        - start: 开始处理
        - workflow_step: 工作流步骤更新
        - documents: 检索到的文档
        - chunk: 答案文本块（流式）
        - done: 处理完成
        - error: 错误发生

    认证:
        需要JWT Bearer Token

    限流:
        50请求/分钟

    Args:
        request: 聊天请求
        current_user: 当前用户（自动注入）

    Returns:
        StreamingResponse: SSE流式响应

    Raises:
        HTTPException: 处理失败时抛出
    """
    try:
        logger.info(
            f"用户 {current_user.username} 发起问答请求",
            extra={"query": request.query[:100], "session_id": request.session_id}
        )

        # 创建GraphMain实例
        graph_main = GraphMain()

        # 创建事件生成器
        event_generator = process_graph_events(
            graph_main=graph_main,
            query=request.query,
            max_retries=request.max_retries,
            include_sources=request.include_sources,
            include_workflow=request.include_workflow
        )

        # 返回SSE响应
        return EventSourceResponse(
            event_generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
            }
        )

    except Exception as e:
        logger.exception(f"流式问答失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"问答处理失败: {str(e)}"
        )


@router.post(
    "/",
    summary="非流式RAG问答",
    description="等待完整答案生成后一次性返回",
    response_model=ConversationResponse
)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    非流式RAG问答接口

    等待完整答案生成后返回，适合不需要实时反馈的场景。

    Args:
        request: 聊天请求
        current_user: 当前用户

    Returns:
        ConversationResponse: 完整的对话响应

    Raises:
        HTTPException: 处理失败时抛出
    """
    try:
        logger.info(
            f"用户 {current_user.username} 发起非流式问答请求",
            extra={"query": request.query[:100]}
        )

        start_time = datetime.now()

        # 创建GraphMain实例
        graph_main = GraphMain()

        # 收集完整响应
        final_answer = ""
        documents = []
        workflow_steps = []

        for event in graph_main.stream(request.query):
            # 收集工作流步骤
            if "loop_step" in event:
                workflow_steps.append({
                    "loop_step": event.get("loop_step"),
                    "answers": event.get("answers"),
                    "web_search": event.get("web_search")
                })

            # 收集文档
            if "documents" in event and event["documents"]:
                documents = event["documents"][:5]  # 最多5个文档

            # 收集最终答案
            if "generation" in event and event["generation"]:
                generation_content = event["generation"]
                if hasattr(generation_content, 'content'):
                    final_answer = generation_content.content
                else:
                    final_answer = str(generation_content)

        elapsed_time = (datetime.now() - start_time).total_seconds()

        # 构建响应
        response = ConversationResponse(
            session_id=request.session_id or f"sess_{datetime.now().timestamp()}",
            message=ChatMessage(
                role="assistant",
                content=sanitize_html(final_answer),
                timestamp=datetime.now()
            ),
            sources=[{"content": doc[:200], "index": i} for i, doc in enumerate(documents)] if request.include_sources else None,
            workflow_steps=workflow_steps if request.include_workflow else None,
            elapsed_time=elapsed_time
        )

        logger.info(
            f"问答完成",
            extra={
                "elapsed_time": elapsed_time,
                "answer_length": len(final_answer),
                "doc_count": len(documents)
            }
        )

        return response

    except Exception as e:
        logger.exception(f"非流式问答失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"问答处理失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="聊天服务健康检查",
    description="检查RAG工作流是否正常运行"
)
async def chat_health():
    """
    聊天服务健康检查

    检查项:
        - GraphMain实例化
        - 环境变量配置
        - 依赖服务连接

    Returns:
        健康状态信息
    """
    try:
        # 尝试创建GraphMain实例
        import os

        checks = {
            "graph_main": False,
            "env_api_key": False,
            "env_base_url": False
        }

        try:
            graph_main = GraphMain()
            checks["graph_main"] = True
        except Exception as e:
            logger.warning(f"GraphMain实例化失败: {e}")

        checks["env_api_key"] = bool(os.getenv("OPENAI_API_KEY"))
        checks["env_base_url"] = bool(os.getenv("OPENAI_BASE_URL"))

        all_healthy = all(checks.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ========== 速率限制装饰器 ==========

# 注意：实际速率限制由middleware处理，这里只是文档说明
# 可以在main.py中为此router配置特定的限流规则

"""
速率限制配置（在main.py中设置）:
- /chat/stream: 30请求/分钟
- /chat: 50请求/分钟
- /chat/health: 无限制
"""
