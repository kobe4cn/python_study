import { useState, useEffect } from 'react'
import { RoleSelector } from './RoleSelector'
import { PermissionEditor } from './PermissionEditor'
import type { User, UserRole, Permission, CreateUserRequest, UpdateUserRequest } from '@/types'

interface UserFormProps {
  user?: User | null
  onSubmit: (data: CreateUserRequest | UpdateUserRequest) => void
  onCancel: () => void
  isLoading?: boolean
}

interface FormData {
  username: string
  email: string
  password: string
  confirmPassword: string
  full_name: string
  role: UserRole
  permissions: Permission[]
  is_active: boolean
}

/**
 * 用户表单组件 - 创建和编辑用户
 */
export function UserForm({ user, onSubmit, onCancel, isLoading = false }: UserFormProps) {
  const isEdit = !!user

  const [formData, setFormData] = useState<FormData>({
    username: user?.username || '',
    email: user?.email || '',
    password: '',
    confirmPassword: '',
    full_name: user?.full_name || '',
    role: user?.role || 'viewer',
    permissions: user?.permissions || [],
    is_active: user?.is_active ?? true,
  })

  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({})
  const [showPermissions, setShowPermissions] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState(0)

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username,
        email: user.email,
        password: '',
        confirmPassword: '',
        full_name: user.full_name || '',
        role: user.role,
        permissions: user.permissions,
        is_active: user.is_active,
      })
    }
  }, [user])

  // 密码强度检查
  useEffect(() => {
    if (!formData.password) {
      setPasswordStrength(0)
      return
    }

    let strength = 0
    if (formData.password.length >= 8) strength++
    if (/[a-z]/.test(formData.password)) strength++
    if (/[A-Z]/.test(formData.password)) strength++
    if (/[0-9]/.test(formData.password)) strength++
    if (/[^a-zA-Z0-9]/.test(formData.password)) strength++

    setPasswordStrength(strength)
  }, [formData.password])

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {}

    if (!formData.username.trim()) {
      newErrors.username = '用户名不能为空'
    } else if (!/^[a-zA-Z0-9_-]{3,20}$/.test(formData.username)) {
      newErrors.username = '用户名只能包含字母、数字、下划线和连字符，长度3-20字符'
    }

    if (!formData.email.trim()) {
      newErrors.email = '邮箱不能为空'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确'
    }

    if (!isEdit && !formData.password) {
      newErrors.password = '密码不能为空'
    }

    if (formData.password) {
      if (formData.password.length < 8) {
        newErrors.password = '密码至少8个字符'
      }
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = '两次密码不一致'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    const submitData: CreateUserRequest | UpdateUserRequest = {
      email: formData.email,
      full_name: formData.full_name || undefined,
      role: formData.role,
      permissions: formData.permissions,
      is_active: formData.is_active,
    }

    if (!isEdit) {
      ;(submitData as CreateUserRequest).username = formData.username
      ;(submitData as CreateUserRequest).password = formData.password
    } else if (formData.password) {
      ;(submitData as UpdateUserRequest).password = formData.password
    }

    onSubmit(submitData)
  }

  const getPasswordStrengthColor = () => {
    if (passwordStrength <= 1) return 'bg-red-500'
    if (passwordStrength <= 3) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getPasswordStrengthText = () => {
    if (passwordStrength <= 1) return '弱'
    if (passwordStrength <= 3) return '中'
    return '强'
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 基本信息 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">基本信息</h3>

        {/* 用户名 */}
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
            用户名 <span className="text-red-500">*</span>
          </label>
          <input
            id="username"
            type="text"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            disabled={isEdit || isLoading}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.username ? 'border-red-500' : 'border-gray-300'
            } ${isEdit ? 'bg-gray-100 cursor-not-allowed' : ''}`}
            placeholder="请输入用户名"
          />
          {errors.username && (
            <p className="mt-1 text-sm text-red-500">{errors.username}</p>
          )}
          {isEdit && (
            <p className="mt-1 text-xs text-gray-500">用户名创建后不可修改</p>
          )}
        </div>

        {/* 邮箱 */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            邮箱 <span className="text-red-500">*</span>
          </label>
          <input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            disabled={isLoading}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.email ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="请输入邮箱"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-500">{errors.email}</p>
          )}
        </div>

        {/* 全名 */}
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
            全名
          </label>
          <input
            id="full_name"
            type="text"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            disabled={isLoading}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="请输入全名（可选）"
          />
        </div>
      </div>

      {/* 密码 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {isEdit ? '修改密码（可选）' : '设置密码'}
        </h3>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            密码 {!isEdit && <span className="text-red-500">*</span>}
          </label>
          <input
            id="password"
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            disabled={isLoading}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.password ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder={isEdit ? '留空表示不修改密码' : '请输入密码'}
          />
          {errors.password && (
            <p className="mt-1 text-sm text-red-500">{errors.password}</p>
          )}

          {/* 密码强度指示器 */}
          {formData.password && (
            <div className="mt-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${getPasswordStrengthColor()}`}
                    style={{ width: `${(passwordStrength / 5) * 100}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-600">
                  强度: {getPasswordStrengthText()}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                建议：至少8个字符，包含大小写字母、数字和特殊字符
              </p>
            </div>
          )}
        </div>

        {formData.password && (
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
              确认密码 {!isEdit && <span className="text-red-500">*</span>}
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              disabled={isLoading}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="请再次输入密码"
            />
            {errors.confirmPassword && (
              <p className="mt-1 text-sm text-red-500">{errors.confirmPassword}</p>
            )}
          </div>
        )}
      </div>

      {/* 角色和权限 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">角色和权限</h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            选择角色 <span className="text-red-500">*</span>
          </label>
          <RoleSelector
            value={formData.role}
            onChange={(role) => setFormData({ ...formData, role })}
            disabled={isLoading}
            showDescription={true}
          />
        </div>

        {/* 自定义权限 */}
        <div>
          <button
            type="button"
            onClick={() => setShowPermissions(!showPermissions)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            {showPermissions ? '隐藏' : '显示'}自定义权限配置
          </button>

          {showPermissions && (
            <div className="mt-3">
              <PermissionEditor
                selectedRole={formData.role}
                selectedPermissions={formData.permissions}
                onChange={(permissions) => setFormData({ ...formData, permissions })}
                disabled={isLoading}
              />
            </div>
          )}
        </div>
      </div>

      {/* 状态 */}
      <div>
        <label className="flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={formData.is_active}
            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            disabled={isLoading}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span className="ml-2 text-sm font-medium text-gray-700">
            激活用户
          </span>
        </label>
        <p className="mt-1 text-xs text-gray-500">
          禁用的用户将无法登录系统
        </p>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {isLoading ? '保存中...' : isEdit ? '保存修改' : '创建用户'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1 px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          取消
        </button>
      </div>
    </form>
  )
}
