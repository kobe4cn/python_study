/**
 * Chat Types - 聊天相关类型定义
 * ===================================
 *
 * 定义聊天、消息、工作流等相关的TypeScript类型
 *
 * @author AI Assistant
 * @date 2025-10-05
 * @version 1.0
 */

/**
 * 消息角色枚举
 */
export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

/**
 * 工作流节点类型
 */
export enum WorkflowNodeType {
  ROUTE_QUESTION = 'route_question',
  RETRIEVE = 'retrieve',
  GRADE_DOCUMENTS = 'grade_documents',
  GENERATE = 'generate',
  WEB_SEARCH = 'websearch',
  GRADE_GENERATION = 'grade_generation'
}

/**
 * 工作流节点状态
 */
export enum WorkflowStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

/**
 * SSE事件类型
 */
export enum StreamEventType {
  START = 'start',
  WORKFLOW_STEP = 'workflow_step',
  DOCUMENT = 'documents',
  CHUNK = 'chunk',
  DONE = 'done',
  ERROR = 'error'
}

/**
 * 聊天消息接口
 */
export interface ChatMessage {
  id: string
  sessionId?: string
  role: MessageRole
  content: string
  timestamp: Date
  metadata?: {
    workflowSteps?: WorkflowStep[]
    documents?: DocumentSource[]
    streamComplete?: boolean
    error?: string
  }
}

/**
 * 工作流步骤接口
 */
export interface WorkflowStep {
  node: WorkflowNodeType
  status: WorkflowStatus
  loop_step?: number
  answers?: number
  max_retries?: number
  web_search?: 'Yes' | 'No'
  decision?: string
  timestamp: string
}

/**
 * 文档来源接口
 */
export interface DocumentSource {
  content: string
  index: number
  relevanceScore?: number
  source?: 'vectorstore' | 'websearch'
  metadata?: {
    url?: string
    title?: string
    createdAt?: string
  }
}

/**
 * 聊天请求接口
 */
export interface ChatRequest {
  query: string
  session_id?: string
  max_retries?: number
  stream?: boolean
  include_sources?: boolean
  include_workflow?: boolean
}

/**
 * 聊天响应接口（非流式）
 */
export interface ChatResponse {
  session_id: string
  message: ChatMessage
  sources?: DocumentSource[]
  workflow_steps?: WorkflowStep[]
  total_tokens?: number
  elapsed_time?: number
}

/**
 * SSE事件接口
 */
export interface StreamEvent {
  event: StreamEventType
  data: any
}

/**
 * Start事件数据
 */
export interface StartEventData {
  query: string
  timestamp: string
}

/**
 * Workflow Step事件数据
 */
export interface WorkflowStepEventData {
  loop_step: number
  answers: number
  max_retries: number
  web_search: string
  timestamp: string
}

/**
 * Documents事件数据
 */
export interface DocumentsEventData {
  count: number
  documents: DocumentSource[]
  timestamp: string
}

/**
 * Chunk事件数据
 */
export interface ChunkEventData {
  content: string
  total_length: number
  timestamp: string
}

/**
 * Done事件数据
 */
export interface DoneEventData {
  final_answer: string
  status: string
  timestamp: string
}

/**
 * Error事件数据
 */
export interface ErrorEventData {
  error: string
  message: string
  timestamp: string
}

/**
 * 会话接口
 */
export interface Conversation {
  id: string
  title: string
  createdAt: Date
  updatedAt: Date
  messageCount: number
  preview?: string
}

/**
 * 聊天状态接口（用于Zustand store）
 */
export interface ChatState {
  // 当前会话
  currentSessionId: string | null
  setCurrentSessionId: (id: string | null) => void

  // 消息列表
  messages: ChatMessage[]
  addMessage: (message: ChatMessage) => void
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void
  clearMessages: () => void

  // 流式状态
  isStreaming: boolean
  setIsStreaming: (streaming: boolean) => void
  streamingMessageId: string | null
  setStreamingMessageId: (id: string | null) => void
  streamBuffer: string
  appendToStreamBuffer: (chunk: string) => void
  clearStreamBuffer: () => void

  // 工作流状态
  currentWorkflowStep: WorkflowStep | null
  setCurrentWorkflowStep: (step: WorkflowStep | null) => void
  workflowHistory: WorkflowStep[]
  addWorkflowStep: (step: WorkflowStep) => void
  clearWorkflowHistory: () => void

  // 文档来源
  documents: DocumentSource[]
  setDocuments: (docs: DocumentSource[]) => void
  clearDocuments: () => void

  // 错误状态
  error: string | null
  setError: (error: string | null) => void
}

/**
 * 会话历史状态接口
 */
export interface ConversationState {
  conversations: Conversation[]
  loading: boolean
  error: string | null

  fetchConversations: () => Promise<void>
  deleteConversation: (id: string) => Promise<void>
  createConversation: (title: string) => Promise<Conversation>
}
