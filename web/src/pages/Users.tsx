import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUsers } from '@/hooks/useUsers'
import { UserList } from '@/components/users/UserList'
import { UserCard } from '@/components/users/UserCard'
import { UserForm } from '@/components/users/UserForm'
import type { User, UserRole, CreateUserRequest, UpdateUserRequest } from '@/types'

type ViewMode = 'list' | 'grid'

export function Users() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState<UserRole | 'all'>('all')
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all')
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)

  const {
    users,
    total,
    totalPages,
    isLoading,
    createUser,
    updateUser,
    deleteUser,
    toggleActive,
    isCreating,
    isUpdating,
  } = useUsers({
    page,
    page_size: 20,
    search: search || undefined,
    role: roleFilter !== 'all' ? roleFilter : undefined,
    is_active: statusFilter === 'all' ? undefined : statusFilter === 'active',
  })

  const handleCreateUser = (data: CreateUserRequest | UpdateUserRequest) => {
    createUser(data as CreateUserRequest, {
      onSuccess: () => {
        setShowCreateModal(false)
      },
    })
  }

  const handleUpdateUser = (data: CreateUserRequest | UpdateUserRequest) => {
    if (editingUser) {
      updateUser(
        { userId: editingUser.id, data: data as UpdateUserRequest },
        {
          onSuccess: () => {
            setEditingUser(null)
          },
        }
      )
    }
  }

  const handleDeleteUser = (user: User) => {
    if (window.confirm(`确定要删除用户 "${user.username}" 吗？此操作不可撤销。`)) {
      deleteUser(user.id)
    }
  }

  const handleToggleActive = (user: User) => {
    const action = user.is_active ? '禁用' : '激活'
    if (window.confirm(`确定要${action}用户 "${user.username}" 吗？`)) {
      toggleActive({ userId: user.id, isActive: !user.is_active })
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">用户管理</h1>
        <p className="mt-2 text-gray-600">管理系统用户和权限配置</p>
      </div>

      {/* 工具栏 */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* 搜索框 */}
          <div className="flex-1">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索用户名或邮箱..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* 筛选器 */}
          <div className="flex gap-2">
            {/* 角色筛选 */}
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value as UserRole | 'all')}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">全部角色</option>
              <option value="admin">🛡️ 管理员</option>
              <option value="editor">✏️ 编辑者</option>
              <option value="viewer">👁️ 查看者</option>
            </select>

            {/* 状态筛选 */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive')}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">全部状态</option>
              <option value="active">✓ 活跃</option>
              <option value="inactive">✕ 禁用</option>
            </select>

            {/* 视图切换 */}
            <div className="flex border border-gray-300 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-2 ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
                title="列表视图"
              >
                ☰
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-2 border-l ${
                  viewMode === 'grid'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
                title="网格视图"
              >
                ▦
              </button>
            </div>

            {/* 新增用户按钮 */}
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium whitespace-nowrap"
            >
              + 新增用户
            </button>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="mt-4 flex gap-4 text-sm text-gray-600">
          <span>总用户数: <strong>{total}</strong></span>
          <span>•</span>
          <span>活跃用户: <strong>{users.filter(u => u.is_active).length}</strong></span>
          <span>•</span>
          <span>当前页: <strong>{page} / {totalPages}</strong></span>
        </div>
      </div>

      {/* 用户列表 */}
      {viewMode === 'list' ? (
        <UserList
          users={users}
          onEdit={setEditingUser}
          onDelete={handleDeleteUser}
          onToggleActive={handleToggleActive}
          onClick={(user) => navigate(`/users/${user.id}`)}
          isLoading={isLoading}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {isLoading ? (
            <div className="col-span-full flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : users.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <div className="text-6xl mb-4">👥</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">暂无用户</h3>
              <p className="text-gray-500">开始创建第一个用户吧</p>
            </div>
          ) : (
            users.map((user) => (
              <UserCard
                key={user.id}
                user={user}
                onEdit={setEditingUser}
                onDelete={handleDeleteUser}
                onToggleActive={handleToggleActive}
                onClick={(user) => navigate(`/users/${user.id}`)}
              />
            ))
          )}
        </div>
      )}

      {/* 分页 */}
      {totalPages > 1 && (
        <div className="mt-6 flex justify-center gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>

          <div className="flex gap-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum: number
              if (totalPages <= 5) {
                pageNum = i + 1
              } else if (page <= 3) {
                pageNum = i + 1
              } else if (page >= totalPages - 2) {
                pageNum = totalPages - 4 + i
              } else {
                pageNum = page - 2 + i
              }

              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`px-4 py-2 border rounded-lg ${
                    page === pageNum
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {pageNum}
                </button>
              )
            })}
          </div>

          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      )}

      {/* 创建用户模态框 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">创建新用户</h2>
            <UserForm
              onSubmit={handleCreateUser}
              onCancel={() => setShowCreateModal(false)}
              isLoading={isCreating}
            />
          </div>
        </div>
      )}

      {/* 编辑用户模态框 */}
      {editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">编辑用户</h2>
            <UserForm
              user={editingUser}
              onSubmit={handleUpdateUser}
              onCancel={() => setEditingUser(null)}
              isLoading={isUpdating}
            />
          </div>
        </div>
      )}
    </div>
  )
}
