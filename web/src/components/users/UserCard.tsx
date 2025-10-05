import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { UserAvatar } from './UserAvatar'
import type { User } from '@/types'
import { ROLE_LABELS } from '@/types'

interface UserCardProps {
  user: User
  onEdit?: (user: User) => void
  onDelete?: (user: User) => void
  onToggleActive?: (user: User) => void
  onClick?: (user: User) => void
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
 * 用户卡片组件 - 网格视图使用
 */
export function UserCard({ user, onEdit, onDelete, onToggleActive, onClick }: UserCardProps) {
  const handleCardClick = () => {
    if (onClick) {
      onClick(user)
    }
  }

  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-all ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={handleCardClick}
    >
      {/* 头部 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <UserAvatar user={user} size="lg" />
          <div>
            <h3 className="font-semibold text-gray-900">{user.username}</h3>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>

        {/* 状态指示器 */}
        <div>
          {user.is_active ? (
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full">
              ✓ 活跃
            </span>
          ) : (
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
              ✕ 禁用
            </span>
          )}
        </div>
      </div>

      {/* 信息 */}
      <div className="space-y-2 mb-4">
        {user.full_name && (
          <div className="text-sm">
            <span className="text-gray-500">全名:</span>{' '}
            <span className="text-gray-900">{user.full_name}</span>
          </div>
        )}

        <div className="text-sm">
          <span className="text-gray-500">角色:</span>{' '}
          <span
            className={`inline-flex items-center px-2 py-1 rounded border ${
              ROLE_BADGES[user.role]
            }`}
          >
            {ROLE_ICONS[user.role]} {ROLE_LABELS[user.role]}
          </span>
        </div>

        <div className="text-sm">
          <span className="text-gray-500">权限:</span>{' '}
          <span className="text-gray-900">{user.permissions.length} 项</span>
        </div>

        <div className="text-sm text-gray-500">
          创建于 {format(new Date(user.created_at), 'yyyy年MM月dd日', { locale: zhCN })}
        </div>

        {user.last_login && (
          <div className="text-sm text-gray-500">
            最后登录 {format(new Date(user.last_login), 'yyyy年MM月dd日 HH:mm', { locale: zhCN })}
          </div>
        )}
      </div>

      {/* 操作按钮 */}
      {(onEdit || onDelete || onToggleActive) && (
        <div className="flex gap-2 pt-4 border-t border-gray-200">
          {onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onEdit(user)
              }}
              className="flex-1 px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
            >
              编辑
            </button>
          )}

          {onToggleActive && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onToggleActive(user)
              }}
              className={`flex-1 px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                user.is_active
                  ? 'text-gray-600 bg-gray-50 hover:bg-gray-100'
                  : 'text-green-600 bg-green-50 hover:bg-green-100'
              }`}
            >
              {user.is_active ? '禁用' : '激活'}
            </button>
          )}

          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDelete(user)
              }}
              className="flex-1 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded hover:bg-red-100 transition-colors"
            >
              删除
            </button>
          )}
        </div>
      )}
    </div>
  )
}
