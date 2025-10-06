import { useAuthStore } from '@/store/auth'

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
