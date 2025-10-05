import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Search,
  FolderOpen,
  Settings,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/common/Button'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const navItems = [
  {
    title: '仪表板',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    title: '文档管理',
    href: '/documents',
    icon: FileText,
  },
  {
    title: '语义搜索',
    href: '/search',
    icon: Search,
  },
  {
    title: '集合管理',
    href: '/collections',
    icon: FolderOpen,
  },
  {
    title: '设置',
    href: '/settings',
    icon: Settings,
  },
]

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {/* 移动端遮罩层 */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      {/* 侧边栏 */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-full w-64 border-r bg-background transition-transform duration-300 md:sticky md:top-16 md:z-30 md:h-[calc(100vh-4rem)] md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col">
          {/* 移动端关闭按钮 */}
          <div className="flex h-16 items-center justify-between border-b px-4 md:hidden">
            <span className="font-semibold">菜单</span>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* 导航菜单 */}
          <nav className="flex-1 space-y-1 overflow-y-auto p-4">
            {navItems.map((item) => (
              <NavLink
                key={item.href}
                to={item.href}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground',
                    isActive
                      ? 'bg-accent text-accent-foreground'
                      : 'text-muted-foreground'
                  )
                }
              >
                <item.icon className="h-5 w-5" />
                {item.title}
              </NavLink>
            ))}
          </nav>

          {/* 底部信息 */}
          <div className="border-t p-4">
            <div className="text-xs text-muted-foreground">
              <p>版本 1.0.0</p>
              <p className="mt-1">© 2024 RAG文档系统</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
