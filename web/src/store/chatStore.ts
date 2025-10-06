/**
 * Chat Store - 聊天状态管理
 * ===================================
 *
 * 使用Zustand管理全局聊天状态
 *
 * @author AI Assistant
 * @date 2025-10-05
 * @version 1.0
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import type { ChatState } from '../types/chat'

/**
 * 聊天状态Store
 */
export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set) => ({
        // ========== 会话状态 ==========
        currentSessionId: null,
        setCurrentSessionId: (id) => set({ currentSessionId: id }),

        // ========== 消息状态 ==========
        messages: [],

        addMessage: (message) =>
          set((state) => ({
            messages: [...state.messages, message]
          })),

        updateMessage: (id, updates) =>
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === id ? { ...msg, ...updates } : msg
            )
          })),

        clearMessages: () => set({ messages: [] }),

        // ========== 流式状态 ==========
        isStreaming: false,
        setIsStreaming: (streaming) => set({ isStreaming: streaming }),

        streamingMessageId: null,
        setStreamingMessageId: (id) => set({ streamingMessageId: id }),

        streamBuffer: '',
        appendToStreamBuffer: (chunk) =>
          set((state) => ({
            streamBuffer: state.streamBuffer + chunk
          })),

        clearStreamBuffer: () => set({ streamBuffer: '' }),

        // ========== 工作流状态 ==========
        currentWorkflowStep: null,
        setCurrentWorkflowStep: (step) => set({ currentWorkflowStep: step }),

        workflowHistory: [],
        addWorkflowStep: (step) =>
          set((state) => ({
            workflowHistory: [...state.workflowHistory, step]
          })),

        clearWorkflowHistory: () => set({ workflowHistory: [] }),

        // ========== 文档来源 ==========
        documents: [],
        setDocuments: (docs) => set({ documents: docs }),
        clearDocuments: () => set({ documents: [] }),

        // ========== 错误状态 ==========
        error: null,
        setError: (error) => set({ error })
      }),
      {
        name: 'chat-storage',
        // 只持久化部分状态
        partialize: (state) => ({
          currentSessionId: state.currentSessionId,
          messages: state.messages
        })
      }
    ),
    {
      name: 'ChatStore'
    }
  )
)

/**
 * 导出状态选择器（用于性能优化）
 */
export const useChatMessages = () => useChatStore((state) => state.messages)
export const useIsStreaming = () => useChatStore((state) => state.isStreaming)
export const useStreamBuffer = () => useChatStore((state) => state.streamBuffer)
export const useWorkflowHistory = () => useChatStore((state) => state.workflowHistory)
export const useDocuments = () => useChatStore((state) => state.documents)
export const useChatError = () => useChatStore((state) => state.error)

/**
 * 导出action选择器
 */
export const useChatActions = () =>
  useChatStore((state) => ({
    addMessage: state.addMessage,
    updateMessage: state.updateMessage,
    clearMessages: state.clearMessages,
    setIsStreaming: state.setIsStreaming,
    setStreamingMessageId: state.setStreamingMessageId,
    appendToStreamBuffer: state.appendToStreamBuffer,
    clearStreamBuffer: state.clearStreamBuffer,
    setCurrentWorkflowStep: state.setCurrentWorkflowStep,
    addWorkflowStep: state.addWorkflowStep,
    clearWorkflowHistory: state.clearWorkflowHistory,
    setDocuments: state.setDocuments,
    clearDocuments: state.clearDocuments,
    setError: state.setError
  }))
