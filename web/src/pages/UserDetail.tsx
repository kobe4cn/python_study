import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { useUser } from '@/hooks/useUsers'
import { UserAvatar } from '@/components/users/UserAvatar'
import { UserForm } from '@/components/users/UserForm'
import { ROLE_LABELS, ROLE_DESCRIPTIONS, PERMISSION_LABELS } from '@/types'
import type { UpdateUserRequest } from '@/types'

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

export function UserDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user, isLoading } = useUser(id!)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showResetPassword, setShowResetPassword] = useState(false)

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">用户不存在</h2>
          <p className="text-gray-600 mb-6">未找到该用户信息</p>
          <button
            onClick={() => navigate('/users')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            返回用户列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* 返回按钮 */}
      <button
        onClick={() => navigate('/users')}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        ← 返回用户列表
      </button>

      {/* 用户信息卡片 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <UserAvatar user={user} size="xl" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{user.username}</h1>
              <p className="text-gray-600">{user.email}</p>
              {user.full_name && (
                <p className="text-sm text-gray-500 mt-1">{user.full_name}</p>
              )}
            </div>
          </div>

          {/* 状态指示器 */}
          <div>
            {user.is_active ? (
              <span className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-green-700 bg-green-100 rounded-full">
                ✓ 活跃用户
              </span>
            ) : (
              <span className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-full">
                ✕ 已禁用
              </span>
            )}
          </div>
        </div>

        {/* 基本信息 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="text-sm font-medium text-gray-500">角色</label>
            <div className="mt-1">
              <span
                className={`inline-flex items-center px-3 py-1.5 rounded-lg border font-medium ${
                  ROLE_BADGES[user.role]
                }`}
              >
                {ROLE_ICONS[user.role]} {ROLE_LABELS[user.role]}
              </span>
              <p className="text-sm text-gray-500 mt-1">
                {ROLE_DESCRIPTIONS[user.role]}
              </p>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">权限数量</label>
            <p className="mt-1 text-lg font-semibold text-gray-900">
              {user.permissions.length} 项权限
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">创建时间</label>
            <p className="mt-1 text-gray-900">
              {format(new Date(user.created_at), 'yyyy年MM月dd日 HH:mm', { locale: zhCN })}
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-500">最后更新</label>
            <p className="mt-1 text-gray-900">
              {format(new Date(user.updated_at), 'yyyy年MM月dd日 HH:mm', { locale: zhCN })}
            </p>
          </div>

          {user.last_login && (
            <div>
              <label className="text-sm font-medium text-gray-500">最后登录</label>
              <p className="mt-1 text-gray-900">
                {format(new Date(user.last_login), 'yyyy年MM月dd日 HH:mm', { locale: zhCN })}
              </p>
            </div>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-3 pt-6 border-t border-gray-200">
          <button
            onClick={() => setShowEditModal(true)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            编辑信息
          </button>
          <button
            onClick={() => setShowResetPassword(true)}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            重置密码
          </button>
          <button
            className={`px-6 py-2 rounded-lg transition-colors font-medium ${
              user.is_active
                ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
          >
            {user.is_active ? '禁用用户' : '激活用户'}
          </button>
          <button className="px-6 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors font-medium">
            删除用户
          </button>
        </div>
      </div>

      {/* 权限详情 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">权限列表</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {user.permissions.map((permission) => (
            <div
              key={permission}
              className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg"
            >
              <span className="text-green-600">✓</span>
              <div>
                <div className="font-mono text-xs text-gray-500">{permission}</div>
                <div className="text-sm text-gray-900">{PERMISSION_LABELS[permission]}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 最近活动（模拟数据） */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">最近活动</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">📄</span>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">上传文档</p>
              <p className="text-xs text-gray-500">doc1.pdf · 2小时前</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">🔍</span>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">执行搜索</p>
              <p className="text-xs text-gray-500">"AI技术" · 5小时前</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">📁</span>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">创建集合</p>
              <p className="text-xs text-gray-500">"技术文档" · 1天前</p>
            </div>
          </div>
        </div>
      </div>

      {/* 编辑用户模态框 */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">编辑用户</h2>
            <UserForm
              user={user}
              onSubmit={(data) => {
                // TODO: 实现更新逻辑
                console.log('Update user:', data)
                setShowEditModal(false)
              }}
              onCancel={() => setShowEditModal(false)}
            />
          </div>
        </div>
      )}

      {/* 重置密码模态框 */}
      {showResetPassword && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">重置密码</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  新密码
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="请输入新密码"
                />
              </div>
              <div className="flex gap-3">
                <button className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  确认重置
                </button>
                <button
                  onClick={() => setShowResetPassword(false)}
                  className="flex-1 px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
