import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from '@/store/auth'
import { authAPI } from '@/services/api'
import type { LoginRequest, ChangePasswordRequest, User } from '@/types'
import toast from 'react-hot-toast'

export function useAuth() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, token, isAuthenticated, setUser, setToken, logout: logoutStore } = useAuthStore()

  // 获取当前用户信息
  const { data: currentUser, isLoading, isError } = useQuery<User>({
    queryKey: ['auth', 'me'],
    queryFn: authAPI.getCurrentUser,
    enabled: isAuthenticated && !!token,
  })

  // React Query v5: 使用 useEffect 替代 onSuccess/onError
  useEffect(() => {
    if (currentUser) {
      setUser(currentUser)
    }
  }, [currentUser, setUser])

  useEffect(() => {
    if (isError && isAuthenticated) {
      logoutStore()
      navigate('/login')
    }
  }, [isError, isAuthenticated, logoutStore, navigate])

  // 登录
  const loginMutation = useMutation({
    mutationFn: (request: LoginRequest) => authAPI.login(request),
    onSuccess: (data) => {
      setToken(data.token)
      setUser(data.user)
      toast.success('登录成功')
      navigate('/')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '登录失败')
    },
  })

  // 登出
  const logoutMutation = useMutation({
    mutationFn: authAPI.logout,
    onSuccess: () => {
      logoutStore()
      queryClient.clear()
      toast.success('已退出登录')
      navigate('/login')
    },
    onError: () => {
      // 即使API调用失败也要清除本地状态
      logoutStore()
      queryClient.clear()
      navigate('/login')
    },
  })

  // 修改密码
  const changePasswordMutation = useMutation({
    mutationFn: (request: ChangePasswordRequest) => authAPI.changePassword(request),
    onSuccess: () => {
      toast.success('密码修改成功，请重新登录')
      logoutMutation.mutate()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '密码修改失败')
    },
  })

  return {
    user: currentUser || user,
    isAuthenticated,
    isLoading,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    changePassword: changePasswordMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
  }
}
