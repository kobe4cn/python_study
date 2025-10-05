import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { Dashboard } from '@/pages/Dashboard'
import { Documents } from '@/pages/Documents'
import { Search } from '@/pages/Search'
import { Collections } from '@/pages/Collections'
import { Login } from '@/pages/Login'
import { Users } from '@/pages/Users'
import { UserDetail } from '@/pages/UserDetail'
import { Profile } from '@/pages/Profile'
import { useAuthStore } from '@/store/auth'

// 创建 React Query 客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5分钟
    },
  },
})

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* 登录页面 */}
          <Route
            path="/login"
            element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
          />

          {/* 受保护的路由 */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />

            {/* 文档管理 */}
            <Route
              path="documents"
              element={
                <ProtectedRoute permission="document:read">
                  <Documents />
                </ProtectedRoute>
              }
            />

            {/* 搜索 */}
            <Route
              path="search"
              element={
                <ProtectedRoute permission="search:execute">
                  <Search />
                </ProtectedRoute>
              }
            />

            {/* 集合管理 */}
            <Route
              path="collections"
              element={
                <ProtectedRoute permission="collection:read">
                  <Collections />
                </ProtectedRoute>
              }
            />

            {/* 用户管理 */}
            <Route
              path="users"
              element={
                <ProtectedRoute permission="user:manage">
                  <Users />
                </ProtectedRoute>
              }
            />

            {/* 用户详情 */}
            <Route
              path="users/:id"
              element={
                <ProtectedRoute permission="user:manage">
                  <UserDetail />
                </ProtectedRoute>
              }
            />

            {/* 个人资料 */}
            <Route path="profile" element={<Profile />} />
          </Route>

          {/* 404 页面 */}
          <Route
            path="*"
            element={
              <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <div className="text-center">
                  <div className="text-6xl mb-4">404</div>
                  <h1 className="text-2xl font-bold text-gray-800 mb-2">页面未找到</h1>
                  <p className="text-gray-600 mb-6">您访问的页面不存在</p>
                  <a
                    href="/"
                    className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    返回首页
                  </a>
                </div>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>

      {/* Toast 通知 */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#fff',
            color: '#333',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </QueryClientProvider>
  )
}

export default App
