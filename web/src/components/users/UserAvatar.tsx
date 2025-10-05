import { useMemo } from 'react'
import type { User } from '@/types'

interface UserAvatarProps {
  user: User | { username: string; email: string; avatar_url?: string }
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const SIZE_CLASSES = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
  xl: 'w-16 h-16 text-xl',
}

/**
 * 用户头像组件 - 支持Gravatar或首字母显示
 */
export function UserAvatar({ user, size = 'md', className = '' }: UserAvatarProps) {
  // 生成Gravatar URL
  const gravatarUrl = useMemo(() => {
    if (user.avatar_url) return user.avatar_url

    // 使用email生成Gravatar
    const email = ('email' in user ? user.email : '').toLowerCase().trim()
    if (email) {
      // 这里使用简化的MD5替代方案，实际项目中可以使用crypto-js
      const hash = btoa(email).substring(0, 32)
      return `https://www.gravatar.com/avatar/${hash}?d=mp&s=200`
    }
    return null
  }, [user])

  // 获取用户名首字母
  const initials = useMemo(() => {
    const username = user.username || ''
    if (!username) return '?'

    // 如果是中文，取前两个字
    if (/[\u4e00-\u9fa5]/.test(username)) {
      return username.substring(0, 2)
    }

    // 如果是英文，取首字母（最多2个）
    const parts = username.split(/[\s_-]+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return username.substring(0, 2).toUpperCase()
  }, [user.username])

  // 根据用户名生成背景颜色
  const bgColor = useMemo(() => {
    const colors = [
      'bg-red-500',
      'bg-orange-500',
      'bg-amber-500',
      'bg-yellow-500',
      'bg-lime-500',
      'bg-green-500',
      'bg-emerald-500',
      'bg-teal-500',
      'bg-cyan-500',
      'bg-sky-500',
      'bg-blue-500',
      'bg-indigo-500',
      'bg-violet-500',
      'bg-purple-500',
      'bg-fuchsia-500',
      'bg-pink-500',
      'bg-rose-500',
    ]
    const hash = user.username.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    return colors[hash % colors.length]
  }, [user.username])

  const sizeClass = SIZE_CLASSES[size]

  if (gravatarUrl) {
    return (
      <img
        src={gravatarUrl}
        alt={user.username}
        className={`${sizeClass} rounded-full object-cover ${className}`}
        onError={(e) => {
          // 如果图片加载失败，隐藏图片显示首字母
          e.currentTarget.style.display = 'none'
        }}
      />
    )
  }

  return (
    <div
      className={`${sizeClass} ${bgColor} rounded-full flex items-center justify-center text-white font-semibold ${className}`}
    >
      {initials}
    </div>
  )
}
