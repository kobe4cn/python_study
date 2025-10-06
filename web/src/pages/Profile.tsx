import { useState } from 'react'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { useAuth } from '@/hooks/useAuth'
import { UserAvatar } from '@/components/users/UserAvatar'
import { ROLE_LABELS, ROLE_DESCRIPTIONS, PERMISSION_LABELS } from '@/types'
import type { ChangePasswordRequest, UserRole } from '@/types'

const ROLE_BADGES: Record<UserRole, string> = {
  admin: 'bg-red-100 text-red-800 border-red-300',
  editor: 'bg-blue-100 text-blue-800 border-blue-300',
  viewer: 'bg-gray-100 text-gray-800 border-gray-300',
}

const ROLE_ICONS: Record<UserRole, string> = {
  admin: '🛡️',
  editor: '✏️',
  viewer: '👁️',
}

export function Profile() {
  const { user, changePassword } = useAuth()
  const [activeTab, setActiveTab] = useState<'info' | 'security'>('info')
  const [isEditingInfo, setIsEditingInfo] = useState(false)
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string>>({})

  const [infoForm, setInfoForm] = useState({
    email: user?.email || '',
    full_name: user?.full_name || '',
  })

  if (!user) {
    return null
  }

  const handleUpdateInfo = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: 实现个人信息更新逻辑
    console.log('Update info:', infoForm)
    setIsEditingInfo(false)
  }

  const validatePasswordForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!passwordForm.old_password) {
      errors.old_password = '请输入当前密码'
    }

    if (!passwordForm.new_password) {
      errors.new_password = '请输入新密码'
    } else if (passwordForm.new_password.length < 8) {
      errors.new_password = '密码至少8个字符'
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      errors.confirm_password = '两次密码不一致'
    }

    setPasswordErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validatePasswordForm()) {
      return
    }

    const request: ChangePasswordRequest = {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    }

    changePassword(request)
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">个人资料</h1>
        <p className="mt-2 text-gray-600">查看和管理您的个人信息</p>
      </div>

      {/* 用户信息卡片 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center gap-4 mb-6">
          <UserAvatar user={user} size="xl" />
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900">{user.username}</h2>
            <p className="text-gray-600">{user.email}</p>
            {user.full_name && (
              <p className="text-sm text-gray-500 mt-1">{user.full_name}</p>
            )}
          </div>
          <div>
            <span
              className={`inline-flex items-center px-3 py-1.5 rounded-lg border font-medium ${
                ROLE_BADGES[user.role]
              }`}
            >
              {ROLE_ICONS[user.role]} {ROLE_LABELS[user.role]}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500 mb-1">角色</div>
            <div className="font-semibold text-gray-900">{ROLE_LABELS[user.role]}</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500 mb-1">权限数</div>
            <div className="font-semibold text-gray-900">{user.permissions.length} 项</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500 mb-1">注册时间</div>
            <div className="font-semibold text-gray-900">
              {format(new Date(user.created_at), 'yyyy-MM-dd', { locale: zhCN })}
            </div>
          </div>
        </div>
      </div>

      {/* 标签页 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {/* 标签头 */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('info')}
            className={`flex-1 px-6 py-3 font-medium transition-colors ${
              activeTab === 'info'
                ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            基本信息
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`flex-1 px-6 py-3 font-medium transition-colors ${
              activeTab === 'security'
                ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            安全设置
          </button>
        </div>

        {/* 标签内容 */}
        <div className="p-6">
          {activeTab === 'info' ? (
            /* 基本信息 */
            <div className="space-y-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">个人信息</h3>
                {!isEditingInfo && (
                  <button
                    onClick={() => setIsEditingInfo(true)}
                    className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100"
                  >
                    编辑信息
                  </button>
                )}
              </div>

              {isEditingInfo ? (
                <form onSubmit={handleUpdateInfo} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      用户名
                    </label>
                    <input
                      type="text"
                      value={user.username}
                      disabled
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
                    />
                    <p className="text-xs text-gray-500 mt-1">用户名不可修改</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      邮箱
                    </label>
                    <input
                      type="email"
                      value={infoForm.email}
                      onChange={(e) => setInfoForm({ ...infoForm, email: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      全名
                    </label>
                    <input
                      type="text"
                      value={infoForm.full_name}
                      onChange={(e) => setInfoForm({ ...infoForm, full_name: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="请输入您的全名"
                    />
                  </div>

                  <div className="flex gap-3">
                    <button
                      type="submit"
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                    >
                      保存更改
                    </button>
                    <button
                      type="button"
                      onClick={() => setIsEditingInfo(false)}
                      className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
                    >
                      取消
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      用户名
                    </label>
                    <p className="text-gray-900">{user.username}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      邮箱
                    </label>
                    <p className="text-gray-900">{user.email}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      全名
                    </label>
                    <p className="text-gray-900">{user.full_name || '未设置'}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      角色
                    </label>
                    <p className="text-gray-900">{ROLE_LABELS[user.role]}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      {ROLE_DESCRIPTIONS[user.role]}
                    </p>
                  </div>
                </div>
              )}

              {/* 权限列表 */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">我的权限</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {user.permissions.map((permission) => (
                    <div
                      key={permission}
                      className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200"
                    >
                      <span className="text-green-600">✓</span>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900">
                          {PERMISSION_LABELS[permission]}
                        </div>
                        <div className="text-xs text-gray-500 font-mono">{permission}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* 安全设置 */
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">修改密码</h3>
                <form onSubmit={handleChangePassword} className="space-y-4 max-w-lg">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      当前密码
                    </label>
                    <input
                      type="password"
                      value={passwordForm.old_password}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, old_password: e.target.value })
                      }
                      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        passwordErrors.old_password ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="请输入当前密码"
                    />
                    {passwordErrors.old_password && (
                      <p className="mt-1 text-sm text-red-500">{passwordErrors.old_password}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      新密码
                    </label>
                    <input
                      type="password"
                      value={passwordForm.new_password}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, new_password: e.target.value })
                      }
                      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        passwordErrors.new_password ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="请输入新密码"
                    />
                    {passwordErrors.new_password && (
                      <p className="mt-1 text-sm text-red-500">{passwordErrors.new_password}</p>
                    )}
                    <p className="mt-1 text-xs text-gray-500">
                      至少8个字符，建议包含大小写字母、数字和特殊字符
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      确认新密码
                    </label>
                    <input
                      type="password"
                      value={passwordForm.confirm_password}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, confirm_password: e.target.value })
                      }
                      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        passwordErrors.confirm_password ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="请再次输入新密码"
                    />
                    {passwordErrors.confirm_password && (
                      <p className="mt-1 text-sm text-red-500">
                        {passwordErrors.confirm_password}
                      </p>
                    )}
                  </div>

                  <button
                    type="submit"
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                  >
                    修改密码
                  </button>
                </form>
              </div>

              <div className="pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">账户信息</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">账户状态</p>
                      <p className="text-sm text-gray-500">您的账户当前处于活跃状态</p>
                    </div>
                    <span className="inline-flex items-center px-3 py-1 text-sm font-medium bg-green-100 text-green-800 rounded-full">
                      ✓ 活跃
                    </span>
                  </div>

                  {user.last_login && (
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">最后登录</p>
                        <p className="text-sm text-gray-500">
                          {format(new Date(user.last_login), 'yyyy年MM月dd日 HH:mm', {
                            locale: zhCN,
                          })}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">注册时间</p>
                      <p className="text-sm text-gray-500">
                        {format(new Date(user.created_at), 'yyyy年MM月dd日', { locale: zhCN })}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
