import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, Permission } from '@/types'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // Actions
  setUser: (user: User) => void
  setToken: (token: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
  hasPermission: (permission: Permission) => boolean
  hasAnyPermission: (permissions: Permission[]) => boolean
  hasAllPermissions: (permissions: Permission[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => {
        set({ user, isAuthenticated: true })
      },

      setToken: (token) => {
        set({ token })
        localStorage.setItem('auth_token', token)
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
        localStorage.removeItem('auth_token')
      },

      updateUser: (updatedFields) => {
        const currentUser = get().user
        if (currentUser) {
          set({ user: { ...currentUser, ...updatedFields } })
        }
      },

      hasPermission: (permission) => {
        const user = get().user
        if (!user) return false
        return user.permissions.includes(permission)
      },

      hasAnyPermission: (permissions) => {
        const user = get().user
        if (!user) return false
        return permissions.some(permission => user.permissions.includes(permission))
      },

      hasAllPermissions: (permissions) => {
        const user = get().user
        if (!user) return false
        return permissions.every(permission => user.permissions.includes(permission))
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
