import { ReactNode } from 'react'
import { usePermissions } from '@/hooks/usePermissions'
import type { Permission } from '@/types'

interface PermissionGuardProps {
  permission?: Permission
  permissions?: Permission[]
  requireAll?: boolean  // true: 需要所有权限, false: 只需任一权限
  fallback?: ReactNode
  children: ReactNode
}

/**
 * 权限守卫组件 - 根据权限条件渲染子组件
 *
 * @example
 * // 单个权限
 * <PermissionGuard permission="document:create">
 *   <Button>上传文档</Button>
 * </PermissionGuard>
 *
 * @example
 * // 多个权限（任一满足）
 * <PermissionGuard permissions={["document:update", "document:delete"]}>
 *   <Button>编辑</Button>
 * </PermissionGuard>
 *
 * @example
 * // 多个权限（全部满足）
 * <PermissionGuard permissions={["document:update", "user:manage"]} requireAll>
 *   <Button>高级操作</Button>
 * </PermissionGuard>
 */
export function PermissionGuard({
  permission,
  permissions,
  requireAll = false,
  fallback = null,
  children,
}: PermissionGuardProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermissions()

  let hasAccess = false

  if (permission) {
    hasAccess = hasPermission(permission)
  } else if (permissions && permissions.length > 0) {
    hasAccess = requireAll
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions)
  } else {
    // 如果没有指定任何权限，默认显示
    hasAccess = true
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>
}
