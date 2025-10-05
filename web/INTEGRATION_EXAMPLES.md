# 权限系统集成示例

本文档展示如何在现有组件中集成用户权限管理系统。

## 📋 目录

1. [在Header中显示用户信息](#在header中显示用户信息)
2. [在Sidebar中添加权限控制](#在sidebar中添加权限控制)
3. [在文档列表中添加权限按钮](#在文档列表中添加权限按钮)
4. [在搜索页面中添加权限检查](#在搜索页面中添加权限检查)

## 1. 在Header中显示用户信息

更新 `components/layout/Header.tsx`:

```tsx
import { useAuth } from '@/hooks/useAuth'
import { UserAvatar } from '@/components/users/UserAvatar'
import { useNavigate } from 'react-router-dom'

export function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <h1 className="text-xl font-bold">RAG 文档系统</h1>

        {/* 用户菜单 */}
        <div className="flex items-center gap-4">
          {user && (
            <>
              <button
                onClick={() => navigate('/profile')}
                className="flex items-center gap-2 hover:bg-gray-100 rounded-lg px-3 py-2 transition-colors"
              >
                <UserAvatar user={user} size="sm" />
                <div className="text-left">
                  <div className="text-sm font-medium text-gray-900">
                    {user.username}
                  </div>
                  <div className="text-xs text-gray-500">{user.email}</div>
                </div>
              </button>

              <button
                onClick={() => logout()}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                退出登录
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
```

## 2. 在Sidebar中添加权限控制

更新 `components/layout/Sidebar.tsx`:

```tsx
import { NavLink } from 'react-router-dom'
import { usePermissions } from '@/hooks/usePermissions'

export function Sidebar() {
  const { hasPermission } = usePermissions()

  const navItems = [
    { path: '/', label: '仪表板', icon: '📊', permission: null },
    { path: '/documents', label: '文档管理', icon: '📄', permission: 'document:read' },
    { path: '/search', label: '搜索', icon: '🔍', permission: 'search:execute' },
    { path: '/collections', label: '集合管理', icon: '📁', permission: 'collection:read' },
    { path: '/users', label: '用户管理', icon: '👥', permission: 'user:manage' },
  ]

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <nav className="p-4 space-y-2">
        {navItems.map((item) => {
          // 检查权限
          if (item.permission && !hasPermission(item.permission as any)) {
            return null
          }

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-600 font-medium'
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <span className="text-xl">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}
```

## 3. 在文档列表中添加权限按钮

更新 `components/documents/DocumentList.tsx`:

```tsx
import { PermissionGuard } from '@/components/auth/PermissionGuard'
import type { Document } from '@/types'

interface DocumentListProps {
  documents: Document[]
  onDelete: (id: string) => void
  onUpdate: (id: string) => void
}

export function DocumentList({ documents, onDelete, onUpdate }: DocumentListProps) {
  return (
    <div className="space-y-4">
      {documents.map((doc) => (
        <div key={doc.id} className="bg-white p-4 rounded-lg border">
          <h3 className="font-semibold">{doc.filename}</h3>
          <p className="text-sm text-gray-600">{doc.content.substring(0, 100)}...</p>

          {/* 操作按钮 - 根据权限显示 */}
          <div className="mt-4 flex gap-2">
            {/* 更新按钮 - 需要 document:update 权限 */}
            <PermissionGuard permission="document:update">
              <button
                onClick={() => onUpdate(doc.id)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                编辑
              </button>
            </PermissionGuard>

            {/* 删除按钮 - 需要 document:delete 权限 */}
            <PermissionGuard permission="document:delete">
              <button
                onClick={() => onDelete(doc.id)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                删除
              </button>
            </PermissionGuard>

            {/* 查看按钮 - 所有人都可以（document:read） */}
            <PermissionGuard permission="document:read">
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
                查看
              </button>
            </PermissionGuard>
          </div>
        </div>
      ))}
    </div>
  )
}
```

## 4. 在文档上传组件中添加权限检查

更新 `components/documents/DocumentUpload.tsx`:

```tsx
import { usePermissions } from '@/hooks/usePermissions'

export function DocumentUpload() {
  const { hasPermission } = usePermissions()

  // 检查是否有上传权限
  if (!hasPermission('document:create')) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <div className="text-6xl mb-4">🔒</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">无上传权限</h3>
        <p className="text-gray-600">您没有权限上传文档</p>
      </div>
    )
  }

  return (
    <div className="bg-white p-6 rounded-lg border">
      <h2 className="text-xl font-bold mb-4">上传文档</h2>
      {/* 上传表单 */}
    </div>
  )
}
```

## 5. 在Dashboard中显示基于权限的统计卡片

更新 `pages/Dashboard.tsx`:

```tsx
import { usePermissions } from '@/hooks/usePermissions'
import { useAuth } from '@/hooks/useAuth'

export function Dashboard() {
  const { user } = useAuth()
  const { hasPermission } = usePermissions()

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">仪表板</h1>

      {/* 欢迎消息 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-blue-900 mb-2">
          欢迎回来，{user?.full_name || user?.username}！
        </h2>
        <p className="text-blue-700">
          您当前的角色是：{user?.role} | 拥有 {user?.permissions.length} 项权限
        </p>
      </div>

      {/* 统计卡片 - 根据权限显示 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {hasPermission('document:read') && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">文档总数</p>
                <p className="text-2xl font-bold text-gray-900">128</p>
              </div>
              <div className="text-4xl">📄</div>
            </div>
          </div>
        )}

        {hasPermission('collection:read') && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">集合总数</p>
                <p className="text-2xl font-bold text-gray-900">12</p>
              </div>
              <div className="text-4xl">📁</div>
            </div>
          </div>
        )}

        {hasPermission('search:execute') && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">搜索次数</p>
                <p className="text-2xl font-bold text-gray-900">1,234</p>
              </div>
              <div className="text-4xl">🔍</div>
            </div>
          </div>
        )}

        {hasPermission('user:manage') && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">用户总数</p>
                <p className="text-2xl font-bold text-gray-900">45</p>
              </div>
              <div className="text-4xl">👥</div>
            </div>
          </div>
        )}
      </div>

      {/* 快捷操作 - 根据权限显示 */}
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">快捷操作</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {hasPermission('document:create') && (
            <button className="p-6 bg-white rounded-lg border hover:shadow-md transition-shadow text-left">
              <div className="text-3xl mb-2">📤</div>
              <h3 className="font-semibold mb-1">上传文档</h3>
              <p className="text-sm text-gray-600">添加新的文档到系统</p>
            </button>
          )}

          {hasPermission('collection:create') && (
            <button className="p-6 bg-white rounded-lg border hover:shadow-md transition-shadow text-left">
              <div className="text-3xl mb-2">➕</div>
              <h3 className="font-semibold mb-1">创建集合</h3>
              <p className="text-sm text-gray-600">创建新的文档集合</p>
            </button>
          )}

          {hasPermission('user:manage') && (
            <button className="p-6 bg-white rounded-lg border hover:shadow-md transition-shadow text-left">
              <div className="text-3xl mb-2">👤</div>
              <h3 className="font-semibold mb-1">管理用户</h3>
              <p className="text-sm text-gray-600">添加或编辑用户</p>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
```

## 6. 在搜索页面中添加权限检查

更新 `pages/Search.tsx`:

```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { usePermissions } from '@/hooks/usePermissions'

export function Search() {
  const { hasPermission } = usePermissions()

  // 页面级权限检查（虽然路由已经保护，这是额外的检查）
  if (!hasPermission('search:execute')) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-6xl mb-4">🔒</div>
        <h1 className="text-2xl font-bold mb-2">无搜索权限</h1>
        <p className="text-gray-600">您没有权限执行搜索操作</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">文档搜索</h1>
      {/* 搜索界面 */}
    </div>
  )
}
```

## 7. 在集合管理中添加条件渲染

更新 `pages/Collections.tsx`:

```tsx
import { PermissionGuard } from '@/components/auth/PermissionGuard'
import { usePermissions } from '@/hooks/usePermissions'

export function Collections() {
  const { hasPermission, hasAnyPermission } = usePermissions()

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">集合管理</h1>

        {/* 创建集合按钮 - 需要权限 */}
        <PermissionGuard permission="collection:create">
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            + 创建集合
          </button>
        </PermissionGuard>
      </div>

      {/* 集合列表 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {collections.map((collection) => (
          <div key={collection.id} className="bg-white p-6 rounded-lg border">
            <h3 className="font-semibold mb-2">{collection.name}</h3>
            <p className="text-sm text-gray-600 mb-4">{collection.description}</p>

            {/* 操作按钮 */}
            <div className="flex gap-2">
              {/* 查看 - 所有人 */}
              <button className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                查看
              </button>

              {/* 删除 - 需要权限 */}
              <PermissionGuard permission="collection:delete">
                <button className="px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200">
                  删除
                </button>
              </PermissionGuard>
            </div>
          </div>
        ))}
      </div>

      {/* 提示信息 - 根据权限显示 */}
      {!hasPermission('collection:create') && (
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            💡 提示：您当前没有创建集合的权限。如需创建集合，请联系管理员。
          </p>
        </div>
      )}
    </div>
  )
}
```

## 8. 使用usePermissions Hook的高级示例

```tsx
import { usePermissions } from '@/hooks/usePermissions'

export function AdvancedExample() {
  const { hasPermission, hasAnyPermission, hasAllPermissions, permissions, role } = usePermissions()

  // 单个权限检查
  const canCreateDoc = hasPermission('document:create')

  // 多个权限检查（任一满足）
  const canModifyDoc = hasAnyPermission(['document:update', 'document:delete'])

  // 多个权限检查（全部满足）
  const canFullManage = hasAllPermissions(['document:create', 'document:update', 'document:delete'])

  // 基于角色的逻辑
  const isAdmin = role === 'admin'

  // 基于权限数组的逻辑
  const hasLimitedAccess = permissions.length < 5

  return (
    <div>
      {canCreateDoc && <button>创建文档</button>}
      {canModifyDoc && <button>编辑文档</button>}
      {canFullManage && <button>完全管理</button>}

      {isAdmin && <div>管理员专属功能</div>}

      {hasLimitedAccess && (
        <div className="bg-yellow-50 p-4 rounded">
          您的权限有限，部分功能可能无法使用
        </div>
      )}

      <div>
        <h3>您的权限列表：</h3>
        <ul>
          {permissions.map((perm) => (
            <li key={perm}>{perm}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
```

## 9. 表单提交前的权限验证

```tsx
import { usePermissions } from '@/hooks/usePermissions'
import toast from 'react-hot-toast'

export function DocumentForm() {
  const { hasPermission } = usePermissions()

  const handleSubmit = async (data: any) => {
    // 提交前验证权限
    if (!hasPermission('document:create')) {
      toast.error('您没有权限创建文档')
      return
    }

    try {
      await createDocument(data)
      toast.success('文档创建成功')
    } catch (error) {
      toast.error('文档创建失败')
    }
  }

  return <form onSubmit={handleSubmit}>{/* 表单内容 */}</form>
}
```

## 10. 动态菜单生成

```tsx
import { usePermissions } from '@/hooks/usePermissions'
import type { Permission } from '@/types'

interface MenuItem {
  label: string
  path: string
  permission?: Permission
  children?: MenuItem[]
}

const menuItems: MenuItem[] = [
  { label: '首页', path: '/' },
  {
    label: '文档',
    path: '/documents',
    permission: 'document:read',
    children: [
      { label: '上传文档', path: '/documents/upload', permission: 'document:create' },
      { label: '文档列表', path: '/documents/list', permission: 'document:read' },
    ],
  },
  { label: '搜索', path: '/search', permission: 'search:execute' },
  { label: '用户管理', path: '/users', permission: 'user:manage' },
]

export function DynamicMenu() {
  const { hasPermission } = usePermissions()

  const filterMenuItems = (items: MenuItem[]): MenuItem[] => {
    return items.filter((item) => {
      // 如果没有权限要求，显示
      if (!item.permission) return true

      // 检查权限
      if (!hasPermission(item.permission)) return false

      // 递归过滤子菜单
      if (item.children) {
        item.children = filterMenuItems(item.children)
      }

      return true
    })
  }

  const visibleMenuItems = filterMenuItems(menuItems)

  return (
    <nav>
      {visibleMenuItems.map((item) => (
        <div key={item.path}>
          <a href={item.path}>{item.label}</a>
          {item.children && item.children.length > 0 && (
            <div className="ml-4">
              {item.children.map((child) => (
                <a key={child.path} href={child.path}>
                  {child.label}
                </a>
              ))}
            </div>
          )}
        </div>
      ))}
    </nav>
  )
}
```

## 总结

权限系统集成的关键点：

1. **组件级保护**: 使用 `<PermissionGuard>` 组件
2. **路由级保护**: 使用 `<ProtectedRoute>` 组件
3. **逻辑级检查**: 使用 `usePermissions()` Hook
4. **用户信息显示**: 使用 `useAuth()` Hook
5. **UI反馈**: 根据权限显示/隐藏功能

通过这些示例，您可以在任何现有组件中轻松集成权限控制功能。
