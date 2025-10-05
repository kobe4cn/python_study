// 文档类型定义
export interface Document {
  id: string
  filename: string
  content: string
  metadata: DocumentMetadata
  created_at: string
  updated_at: string
  file_size?: number
  file_type?: string
  collection_id?: string
}

export interface DocumentMetadata {
  source?: string
  author?: string
  created_date?: string
  page_count?: number
  [key: string]: any
}

// 文档上传
export interface UploadDocumentRequest {
  file: File
  collection_id?: string
  metadata?: Record<string, any>
}

export interface UploadFromUrlRequest {
  url: string
  collection_id?: string
  metadata?: Record<string, any>
}

export interface UploadResponse {
  document_id: string
  filename: string
  message: string
}

// 搜索相关
export interface SearchRequest {
  query: string
  collection_id?: string
  top_k?: number
  filter?: Record<string, any>
}

export interface SearchResult {
  id: string
  content: string
  metadata: DocumentMetadata
  score: number
  document_id: string
  highlights?: string[]
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
  query: string
  execution_time: number
}

// 集合类型
export interface Collection {
  id: string
  name: string
  description?: string
  document_count: number
  created_at: string
  updated_at: string
  metadata?: Record<string, any>
}

export interface CreateCollectionRequest {
  name: string
  description?: string
  metadata?: Record<string, any>
}

// 统计数据
export interface SystemStats {
  total_documents: number
  total_collections: number
  total_storage_bytes: number
  total_vectors: number
  last_updated: string
}

// API响应通用类型
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginationParams {
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 用户和权限类型
export type UserRole = 'admin' | 'editor' | 'viewer'

export type Permission =
  | 'document:create'
  | 'document:read'
  | 'document:update'
  | 'document:delete'
  | 'collection:create'
  | 'collection:read'
  | 'collection:delete'
  | 'search:execute'
  | 'user:manage'

export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  role: UserRole
  permissions: Permission[]
  is_active: boolean
  created_at: string
  updated_at: string
  last_login?: string
  avatar_url?: string
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  full_name?: string
  role: UserRole
  permissions?: Permission[]
  is_active?: boolean
}

export interface UpdateUserRequest {
  email?: string
  full_name?: string
  role?: UserRole
  permissions?: Permission[]
  is_active?: boolean
  password?: string
}

export interface LoginRequest {
  username: string
  password: string
  remember_me?: boolean
}

export interface LoginResponse {
  token: string
  user: User
  expires_at: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

// 权限配置
export const PERMISSION_LABELS: Record<Permission, string> = {
  'document:create': '创建/上传文档',
  'document:read': '查看文档',
  'document:update': '更新文档',
  'document:delete': '删除文档',
  'collection:create': '创建集合',
  'collection:read': '查看集合',
  'collection:delete': '删除集合',
  'search:execute': '执行搜索',
  'user:manage': '管理用户'
}

export const PERMISSION_GROUPS = {
  document: ['document:create', 'document:read', 'document:update', 'document:delete'] as Permission[],
  collection: ['collection:create', 'collection:read', 'collection:delete'] as Permission[],
  search: ['search:execute'] as Permission[],
  user: ['user:manage'] as Permission[]
}

export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  admin: [
    'document:create', 'document:read', 'document:update', 'document:delete',
    'collection:create', 'collection:read', 'collection:delete',
    'search:execute', 'user:manage'
  ],
  editor: [
    'document:create', 'document:read', 'document:update', 'document:delete',
    'collection:create', 'collection:read', 'collection:delete',
    'search:execute'
  ],
  viewer: ['document:read', 'collection:read', 'search:execute']
}

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: '管理员',
  editor: '编辑者',
  viewer: '查看者'
}

export const ROLE_DESCRIPTIONS: Record<UserRole, string> = {
  admin: '拥有所有权限，可管理用户和系统设置',
  editor: '可管理文档和集合，执行搜索',
  viewer: '只能查看文档和执行搜索'
}

// UI状态类型
export type Theme = 'light' | 'dark'

export interface AppSettings {
  theme: Theme
  api_base_url: string
  default_top_k: number
  enable_animations: boolean
}

// 错误类型
export interface ApiError {
  message: string
  code?: string
  details?: any
}
