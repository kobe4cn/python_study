import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { usePermissions } from '@/hooks/usePermissions'
import type { Permission } from '@/types'

interface ProtectedRouteProps {
  permission?: Permission
  permissions?: Permission[]
  requireAll?: boolean
  redirectTo?: string
  children: ReactNode
}

/**
 * 路由保护组件 - 根据认证状态和权限保护路由
 *
 * @example
 * <Route path="/users" element={
 *   <ProtectedRoute permission="user:manage">
 *     <Users />
 *   </ProtectedRoute>
 * } />
 */
export function ProtectedRoute({
  permission,
  permissions,
  requireAll = false,
  redirectTo = '/login',
  children,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()
  const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermissions()

  // 等待认证状态加载
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // 未登录，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace />
  }

  // 检查权限
  if (permission || permissions) {
    let hasAccess = false

    if (permission) {
      hasAccess = hasPermission(permission)
    } else if (permissions && permissions.length > 0) {
      hasAccess = requireAll
        ? hasAllPermissions(permissions)
        : hasAnyPermission(permissions)
    }

    // 无权限，重定向到首页或显示无权限页面
    if (!hasAccess) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
          <div className="text-center">
            <div className="text-6xl mb-4">🔒</div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">访问受限</h1>
            <p className="text-gray-600 mb-6">您没有权限访问此页面</p>
            <a
              href="/"
              className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              返回首页
            </a>
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
}
