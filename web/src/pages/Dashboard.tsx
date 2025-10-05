import { useQuery } from '@tanstack/react-query'
import { FileText, FolderOpen, Database, TrendingUp, Upload, Search as SearchIcon } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { Loading } from '@/components/common/Loading'
import { statsAPI, documentAPI } from '@/services/api'
import { formatFileSize } from '@/lib/utils'
import { Link } from 'react-router-dom'

export function Dashboard() {
  // 获取系统统计
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: statsAPI.getSystemStats,
  })

  // 获取最近文档
  const { data: recentDocs, isLoading: docsLoading } = useQuery({
    queryKey: ['documents', 'recent'],
    queryFn: () => documentAPI.list({ page: 1, page_size: 5, sort_by: 'created_at', sort_order: 'desc' }),
  })

  if (statsLoading || docsLoading) {
    return <Loading text="加载仪表板..." />
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">仪表板</h1>
        <p className="text-muted-foreground">
          欢迎回来！这是您的文档处理系统概览
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总文档数</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_documents || 0}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3" /> 较上周 +12%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">集合数量</CardTitle>
            <FolderOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_collections || 0}</div>
            <p className="text-xs text-muted-foreground">
              跨 {stats?.total_collections || 0} 个主题
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">向量数量</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_vectors?.toLocaleString() || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              已索引向量
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">存储空间</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatFileSize(stats?.total_storage_bytes || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              总存储使用量
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 快速操作 */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>快速操作</CardTitle>
            <CardDescription>常用功能快速访问</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-2">
            <Link to="/documents">
              <Button variant="outline" className="w-full justify-start">
                <Upload className="mr-2 h-4 w-4" />
                上传新文档
              </Button>
            </Link>
            <Link to="/search">
              <Button variant="outline" className="w-full justify-start">
                <SearchIcon className="mr-2 h-4 w-4" />
                语义搜索
              </Button>
            </Link>
            <Link to="/collections">
              <Button variant="outline" className="w-full justify-start">
                <FolderOpen className="mr-2 h-4 w-4" />
                管理集合
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* 最近文档 */}
        <Card>
          <CardHeader>
            <CardTitle>最近上传</CardTitle>
            <CardDescription>最新的 5 个文档</CardDescription>
          </CardHeader>
          <CardContent>
            {recentDocs && recentDocs.items.length > 0 ? (
              <div className="space-y-3">
                {recentDocs.items.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between rounded-lg border p-3 hover:bg-accent"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium line-clamp-1">
                          {doc.filename}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(doc.created_at).toLocaleDateString('zh-CN')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">暂无文档</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 使用提示 */}
      <Card className="border-primary/50 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-lg">💡 使用提示</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>• 使用快捷键 <kbd className="rounded bg-muted px-2 py-1">⌘K</kbd> 快速打开搜索</p>
          <p>• 支持拖放上传文档，支持 PDF、DOC、DOCX、TXT、MD 格式</p>
          <p>• 使用集合功能组织和管理不同主题的文档</p>
          <p>• 语义搜索基于 RAG 技术，可以找到语义相关的内容</p>
        </CardContent>
      </Card>
    </div>
  )
}
