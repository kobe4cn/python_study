/**
 * Chat Service - 聊天服务
 * ===================================
 *
 * 处理与后端聊天API的通信，包括流式和非流式请求
 *
 * @author AI Assistant
 * @date 2025-10-05
 * @version 1.0
 */

import {
  ChatRequest,
  ChatResponse,
  StreamEvent,
  StreamEventType,
  StartEventData,
  WorkflowStepEventData,
  DocumentsEventData,
  ChunkEventData,
  DoneEventData,
  ErrorEventData
} from '../types/chat'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_V1_PREFIX = '/api/v1'

/**
 * 获取认证token
 */
function getAuthToken(): string | null {
  return localStorage.getItem('access_token')
}

/**
 * 获取请求headers
 */
function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  }

  const token = getAuthToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

/**
 * 聊天服务类
 */
export class ChatService {
  /**
   * 流式聊天请求
   *
   * @param request 聊天请求
   * @param callbacks 事件回调函数
   * @returns Promise<void>
   */
  static async streamChat(
    request: ChatRequest,
    callbacks: {
      onStart?: (data: StartEventData) => void
      onWorkflowStep?: (data: WorkflowStepEventData) => void
      onDocuments?: (data: DocumentsEventData) => void
      onChunk?: (data: ChunkEventData) => void
      onDone?: (data: DoneEventData) => void
      onError?: (data: ErrorEventData) => void
    }
  ): Promise<void> {
    const url = `${API_BASE_URL}${API_V1_PREFIX}/chat/stream`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status} ${response.statusText}`)
      }

      if (!response.body) {
        throw new Error('响应体为空')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        // 解码并追加到缓冲区
        buffer += decoder.decode(value, { stream: true })

        // 处理SSE消息
        const messages = buffer.split('\n\n')
        buffer = messages.pop() || '' // 保留最后一个不完整的消息

        for (const message of messages) {
          if (!message.trim()) continue

          try {
            const event = this.parseSSEMessage(message)
            if (event) {
              this.handleStreamEvent(event, callbacks)
            }
          } catch (error) {
            console.error('解析SSE消息失败:', error, message)
          }
        }
      }
    } catch (error) {
      console.error('流式聊天请求失败:', error)

      if (callbacks.onError) {
        callbacks.onError({
          error: '请求失败',
          message: error instanceof Error ? error.message : String(error),
          timestamp: new Date().toISOString()
        })
      }

      throw error
    }
  }

  /**
   * 解析SSE消息
   */
  private static parseSSEMessage(message: string): StreamEvent | null {
    const lines = message.split('\n')
    let eventType: string | null = null
    let data: string | null = null

    for (const line of lines) {
      if (line.startsWith('event:')) {
        eventType = line.slice(6).trim()
      } else if (line.startsWith('data:')) {
        data = line.slice(5).trim()
      }
    }

    if (!eventType || !data) {
      return null
    }

    try {
      return {
        event: eventType as StreamEventType,
        data: JSON.parse(data)
      }
    } catch (error) {
      console.error('解析JSON数据失败:', error, data)
      return null
    }
  }

  /**
   * 处理流事件
   */
  private static handleStreamEvent(
    event: StreamEvent,
    callbacks: {
      onStart?: (data: StartEventData) => void
      onWorkflowStep?: (data: WorkflowStepEventData) => void
      onDocuments?: (data: DocumentsEventData) => void
      onChunk?: (data: ChunkEventData) => void
      onDone?: (data: DoneEventData) => void
      onError?: (data: ErrorEventData) => void
    }
  ): void {
    switch (event.event) {
      case StreamEventType.START:
        callbacks.onStart?.(event.data as StartEventData)
        break

      case StreamEventType.WORKFLOW_STEP:
        callbacks.onWorkflowStep?.(event.data as WorkflowStepEventData)
        break

      case StreamEventType.DOCUMENT:
        callbacks.onDocuments?.(event.data as DocumentsEventData)
        break

      case StreamEventType.CHUNK:
        callbacks.onChunk?.(event.data as ChunkEventData)
        break

      case StreamEventType.DONE:
        callbacks.onDone?.(event.data as DoneEventData)
        break

      case StreamEventType.ERROR:
        callbacks.onError?.(event.data as ErrorEventData)
        break

      default:
        console.warn('未知事件类型:', event.event)
    }
  }

  /**
   * 非流式聊天请求
   *
   * @param request 聊天请求
   * @returns Promise<ChatResponse>
   */
  static async chat(request: ChatRequest): Promise<ChatResponse> {
    const url = `${API_BASE_URL}${API_V1_PREFIX}/chat`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ ...request, stream: false })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP错误: ${response.status}`)
      }

      const data: ChatResponse = await response.json()
      return data
    } catch (error) {
      console.error('聊天请求失败:', error)
      throw error
    }
  }

  /**
   * 健康检查
   *
   * @returns Promise<boolean>
   */
  static async healthCheck(): Promise<boolean> {
    const url = `${API_BASE_URL}${API_V1_PREFIX}/chat/health`

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: getHeaders()
      })

      if (!response.ok) {
        return false
      }

      const data = await response.json()
      return data.status === 'healthy'
    } catch (error) {
      console.error('健康检查失败:', error)
      return false
    }
  }
}

/**
 * 默认导出
 */
export default ChatService
