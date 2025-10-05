import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { Toaster } from 'react-hot-toast'

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="relative min-h-screen bg-background">
      {/* Header */}
      <Header onMenuClick={() => setSidebarOpen(true)} />

      {/* Main Content */}
      <div className="flex">
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        {/* Page Content */}
        <main className="flex-1">
          <div className="container py-6">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Toast 通知 */}
      <Toaster
        position="top-right"
        toastOptions={{
          className: 'bg-background text-foreground border',
          duration: 3000,
        }}
      />
    </div>
  )
}
