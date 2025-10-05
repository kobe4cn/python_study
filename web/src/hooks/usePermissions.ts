import { useAuthStore } from '@/store/auth'
import type { Permission } from '@/types'

export function usePermissions() {
  const { user, hasPermission, hasAnyPermission, hasAllPermissions } = useAuthStore()

  return {
    user,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    permissions: user?.permissions || [],
    role: user?.role,
  }
}
