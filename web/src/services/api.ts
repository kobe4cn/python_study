import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  Document,
  SearchRequest,
  SearchResponse,
  Collection,
  CreateCollectionRequest,
  UploadResponse,
  SystemStats,
  PaginationParams,
  PaginatedResponse,
} from '@/types'

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证 token
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // 统一错误处理
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，跳转到登录页
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
          break
        case 403:
          console.error('没有权限访问')
          break
        case 404:
          console.error('资源不存在')
          break
        case 500:
          console.error('服务器错误')
          break
        default:
          console.error('请求失败:', error.message)
      }
    }
    return Promise.reject(error)
  }
)

// 文档相关 API
export const documentAPI = {
  /**
   * 上传文档
   */
  upload: async (file: File, collectionId?: string, metadata?: Record<string, any>): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    if (collectionId) formData.append('collection_id', collectionId)
    if (metadata) formData.append('metadata', JSON.stringify(metadata))

    const response = await api.post<UploadResponse>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * 从URL导入文档
   */
  uploadFromUrl: async (url: string, collectionId?: string, metadata?: Record<string, any>): Promise<UploadResponse> => {
    const response = await api.post<UploadResponse>('/documents/from-url', {
      url,
      collection_id: collectionId,
      metadata,
    })
    return response.data
  },

  /**
   * 获取文档列表
   */
  list: async (params?: PaginationParams): Promise<PaginatedResponse<Document>> => {
    const response = await api.get<PaginatedResponse<Document>>('/documents', { params })
    return response.data
  },

  /**
   * 获取文档详情
   */
  get: async (documentId: string): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${documentId}`)
    return response.data
  },

  /**
   * 删除文档
   */
  delete: async (documentId: string): Promise<void> => {
    await api.delete(`/documents/${documentId}`)
  },

  /**
   * 批量删除文档
   */
  bulkDelete: async (documentIds: string[]): Promise<void> => {
    await api.post('/documents/bulk-delete', { document_ids: documentIds })
  },

  /**
   * 更新文档元数据
   */
  updateMetadata: async (documentId: string, metadata: Record<string, any>): Promise<Document> => {
    const response = await api.patch<Document>(`/documents/${documentId}/metadata`, { metadata })
    return response.data
  },
}

// 搜索相关 API
export const searchAPI = {
  /**
   * 语义搜索
   */
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/search', request)
    return response.data
  },

  /**
   * 获取搜索建议
   */
  suggestions: async (query: string, limit: number = 5): Promise<string[]> => {
    const response = await api.get<string[]>('/search/suggestions', {
      params: { query, limit },
    })
    return response.data
  },
}

// 集合相关 API
export const collectionAPI = {
  /**
   * 获取集合列表
   */
  list: async (): Promise<Collection[]> => {
    const response = await api.get<Collection[]>('/collections')
    return response.data
  },

  /**
   * 创建集合
   */
  create: async (request: CreateCollectionRequest): Promise<Collection> => {
    const response = await api.post<Collection>('/collections', request)
    return response.data
  },

  /**
   * 获取集合详情
   */
  get: async (collectionId: string): Promise<Collection> => {
    const response = await api.get<Collection>(`/collections/${collectionId}`)
    return response.data
  },

  /**
   * 删除集合
   */
  delete: async (collectionId: string): Promise<void> => {
    await api.delete(`/collections/${collectionId}`)
  },

  /**
   * 更新集合
   */
  update: async (collectionId: string, data: Partial<CreateCollectionRequest>): Promise<Collection> => {
    const response = await api.patch<Collection>(`/collections/${collectionId}`, data)
    return response.data
  },

  /**
   * 获取集合中的文档
   */
  getDocuments: async (collectionId: string, params?: PaginationParams): Promise<PaginatedResponse<Document>> => {
    const response = await api.get<PaginatedResponse<Document>>(`/collections/${collectionId}/documents`, { params })
    return response.data
  },
}

// 系统统计 API
export const statsAPI = {
  /**
   * 获取系统统计信息
   */
  getSystemStats: async (): Promise<SystemStats> => {
    const response = await api.get<SystemStats>('/stats')
    return response.data
  },
}

// 用户认证 API
export const authAPI = {
  /**
   * 用户登录
   */
  login: async (request: import('@/types').LoginRequest): Promise<import('@/types').LoginResponse> => {
    const response = await api.post<import('@/types').LoginResponse>('/auth/login', request)
    return response.data
  },

  /**
   * 用户登出
   */
  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async (): Promise<import('@/types').User> => {
    const response = await api.get<import('@/types').User>('/auth/me')
    return response.data
  },

  /**
   * 修改密码
   */
  changePassword: async (request: import('@/types').ChangePasswordRequest): Promise<void> => {
    await api.post('/auth/change-password', request)
  },
}

// 用户管理 API
export const userAPI = {
  /**
   * 获取用户列表
   */
  list: async (params?: PaginationParams & {
    search?: string
    role?: string
    is_active?: boolean
  }): Promise<PaginatedResponse<import('@/types').User>> => {
    const response = await api.get<PaginatedResponse<import('@/types').User>>('/users', { params })
    return response.data
  },

  /**
   * 获取用户详情
   */
  get: async (userId: string): Promise<import('@/types').User> => {
    const response = await api.get<import('@/types').User>(`/users/${userId}`)
    return response.data
  },

  /**
   * 创建用户
   */
  create: async (request: import('@/types').CreateUserRequest): Promise<import('@/types').User> => {
    const response = await api.post<import('@/types').User>('/users', request)
    return response.data
  },

  /**
   * 更新用户
   */
  update: async (userId: string, request: import('@/types').UpdateUserRequest): Promise<import('@/types').User> => {
    const response = await api.patch<import('@/types').User>(`/users/${userId}`, request)
    return response.data
  },

  /**
   * 删除用户
   */
  delete: async (userId: string): Promise<void> => {
    await api.delete(`/users/${userId}`)
  },

  /**
   * 激活/禁用用户
   */
  toggleActive: async (userId: string, isActive: boolean): Promise<import('@/types').User> => {
    const response = await api.patch<import('@/types').User>(`/users/${userId}/active`, { is_active: isActive })
    return response.data
  },

  /**
   * 重置用户密码
   */
  resetPassword: async (userId: string, newPassword: string): Promise<void> => {
    await api.post(`/users/${userId}/reset-password`, { new_password: newPassword })
  },
}

export default api
