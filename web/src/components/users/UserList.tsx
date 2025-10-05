import { useState } from 'react'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { UserAvatar } from './UserAvatar'
import type { User } from '@/types'
import { ROLE_LABELS } from '@/types'

interface UserListProps {
  users: User[]
  onEdit?: (user: User) => void
  onDelete?: (user: User) => void
  onToggleActive?: (user: User) => void
  onClick?: (user: User) => void
  isLoading?: boolean
}

const ROLE_BADGES = {
  admin: 'bg-red-100 text-red-800 border-red-300',
  editor: 'bg-blue-100 text-blue-800 border-blue-300',
  viewer: 'bg-gray-100 text-gray-800 border-gray-300',
}

const ROLE_ICONS = {
  admin: '🛡️',
  editor: '✏️',
  viewer: '👁️',
}

/**
 * 用户列表组件 - 表格视图
 */
export function UserList({
  users,
  onEdit,
  onDelete,
  onToggleActive,
  onClick,
  isLoading,
}: UserListProps) {
  const [selectedUsers, setSelectedUsers] = useState<string[]>([])

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedUsers(users.map((u) => u.id))
    } else {
      setSelectedUsers([])
    }
  }

  const handleSelectUser = (userId: string) => {
    setSelectedUsers((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    )
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (users.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">👥</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">暂无用户</h3>
        <p className="text-gray-500">开始创建第一个用户吧</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="w-12 px-6 py-3">
                <input
                  type="checkbox"
                  checked={selectedUsers.length === users.length}
                  onChange={handleSelectAll}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                用户
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                角色
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                权限数
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                状态
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                创建时间
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                最后登录
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr
                key={user.id}
                className={`hover:bg-gray-50 transition-colors ${
                  onClick ? 'cursor-pointer' : ''
                }`}
                onClick={() => onClick?.(user)}
              >
                <td className="px-6 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={selectedUsers.includes(user.id)}
                    onChange={() => handleSelectUser(user.id)}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <UserAvatar user={user} size="sm" />
                    <div className="ml-3">
                      <div className="text-sm font-medium text-gray-900">
                        {user.username}
                      </div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                      {user.full_name && (
                        <div className="text-xs text-gray-400">{user.full_name}</div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-md border text-sm font-medium ${
                      ROLE_BADGES[user.role]
                    }`}
                  >
                    {ROLE_ICONS[user.role]} {ROLE_LABELS[user.role]}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {user.permissions.length}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {user.is_active ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ 活跃
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      ✕ 禁用
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {format(new Date(user.created_at), 'yyyy-MM-dd', { locale: zhCN })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.last_login
                    ? format(new Date(user.last_login), 'yyyy-MM-dd HH:mm', { locale: zhCN })
                    : '从未登录'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium" onClick={(e) => e.stopPropagation()}>
                  <div className="flex justify-end gap-2">
                    {onEdit && (
                      <button
                        onClick={() => onEdit(user)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        编辑
                      </button>
                    )}
                    {onToggleActive && (
                      <button
                        onClick={() => onToggleActive(user)}
                        className={user.is_active ? 'text-gray-600 hover:text-gray-900' : 'text-green-600 hover:text-green-900'}
                      >
                        {user.is_active ? '禁用' : '激活'}
                      </button>
                    )}
                    {onDelete && (
                      <button
                        onClick={() => onDelete(user)}
                        className="text-red-600 hover:text-red-900"
                      >
                        删除
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 批量操作栏 */}
      {selectedUsers.length > 0 && (
        <div className="bg-blue-50 border-t border-blue-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-800">
              已选择 {selectedUsers.length} 个用户
            </span>
            <div className="flex gap-2">
              <button className="px-3 py-1 text-sm font-medium text-blue-600 bg-white rounded hover:bg-blue-100 transition-colors">
                批量激活
              </button>
              <button className="px-3 py-1 text-sm font-medium text-red-600 bg-white rounded hover:bg-red-100 transition-colors">
                批量删除
              </button>
              <button
                onClick={() => setSelectedUsers([])}
                className="px-3 py-1 text-sm font-medium text-gray-600 bg-white rounded hover:bg-gray-100 transition-colors"
              >
                取消选择
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
