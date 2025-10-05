import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userAPI } from '@/services/api'
import type { CreateUserRequest, UpdateUserRequest, PaginationParams } from '@/types'
import toast from 'react-hot-toast'

interface UseUsersParams extends PaginationParams {
  search?: string
  role?: string
  is_active?: boolean
}

export function useUsers(params?: UseUsersParams) {
  const queryClient = useQueryClient()

  // 获取用户列表
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['users', params],
    queryFn: () => userAPI.list(params),
  })

  // 创建用户
  const createMutation = useMutation({
    mutationFn: (request: CreateUserRequest) => userAPI.create(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast.success('用户创建成功')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '用户创建失败')
    },
  })

  // 更新用户
  const updateMutation = useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: UpdateUserRequest }) =>
      userAPI.update(userId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast.success('用户更新成功')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '用户更新失败')
    },
  })

  // 删除用户
  const deleteMutation = useMutation({
    mutationFn: (userId: string) => userAPI.delete(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast.success('用户删除成功')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '用户删除失败')
    },
  })

  // 激活/禁用用户
  const toggleActiveMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      userAPI.toggleActive(userId, isActive),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast.success(variables.isActive ? '用户已激活' : '用户已禁用')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '操作失败')
    },
  })

  // 重置密码
  const resetPasswordMutation = useMutation({
    mutationFn: ({ userId, newPassword }: { userId: string; newPassword: string }) =>
      userAPI.resetPassword(userId, newPassword),
    onSuccess: () => {
      toast.success('密码重置成功')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '密码重置失败')
    },
  })

  return {
    users: data?.items || [],
    total: data?.total || 0,
    page: data?.page || 1,
    pageSize: data?.page_size || 20,
    totalPages: data?.total_pages || 1,
    isLoading,
    error,
    refetch,
    createUser: createMutation.mutate,
    updateUser: updateMutation.mutate,
    deleteUser: deleteMutation.mutate,
    toggleActive: toggleActiveMutation.mutate,
    resetPassword: resetPasswordMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  }
}

// 获取单个用户详情
export function useUser(userId: string) {
  const queryClient = useQueryClient()

  const { data: user, isLoading, error } = useQuery({
    queryKey: ['users', userId],
    queryFn: () => userAPI.get(userId),
    enabled: !!userId,
  })

  return {
    user,
    isLoading,
    error,
  }
}
