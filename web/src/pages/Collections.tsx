import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, FolderOpen, FileText, Trash2, Calendar } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Loading } from '@/components/common/Loading'
import { collectionAPI } from '@/services/api'
import { formatRelativeTime } from '@/lib/utils'
import toast from 'react-hot-toast'

export function Collections() {
  const [showCreate, setShowCreate] = useState(false)
  const [newCollectionName, setNewCollectionName] = useState('')
  const [newCollectionDesc, setNewCollectionDesc] = useState('')
  const queryClient = useQueryClient()

  // 获取集合列表
  const { data: collections, isLoading } = useQuery({
    queryKey: ['collections'],
    queryFn: collectionAPI.list,
  })

  // 创建集合
  const createMutation = useMutation({
    mutationFn: () =>
      collectionAPI.create({
        name: newCollectionName,
        description: newCollectionDesc,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      toast.success('集合创建成功')
      setShowCreate(false)
      setNewCollectionName('')
      setNewCollectionDesc('')
    },
    onError: () => {
      toast.error('集合创建失败')
    },
  })

  // 删除集合
  const deleteMutation = useMutation({
    mutationFn: (collectionId: string) => collectionAPI.delete(collectionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      toast.success('集合删除成功')
    },
    onError: () => {
      toast.error('集合删除失败')
    },
  })

  const handleCreate = () => {
    if (!newCollectionName.trim()) {
      toast.error('请输入集合名称')
      return
    }
    createMutation.mutate()
  }

  const handleDelete = (collectionId: string, collectionName: string) => {
    if (window.confirm(`确定要删除集合 "${collectionName}" 吗？这将删除集合中的所有文档。`)) {
      deleteMutation.mutate(collectionId)
    }
  }

  if (isLoading) {
    return <Loading text="加载集合..." />
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">集合管理</h1>
          <p className="text-muted-foreground">
            组织和管理您的文档集合
          </p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)}>
          <Plus className="mr-2 h-4 w-4" />
          {showCreate ? '取消' : '创建集合'}
        </Button>
      </div>

      {/* 创建集合表单 */}
      {showCreate && (
        <Card className="p-6">
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium">集合名称</label>
              <Input
                placeholder="例如：技术文档、产品手册等"
                value={newCollectionName}
                onChange={(e) => setNewCollectionName(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium">描述（可选）</label>
              <Input
                placeholder="简要描述这个集合的用途"
                value={newCollectionDesc}
                onChange={(e) => setNewCollectionDesc(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleCreate}
                disabled={createMutation.isPending}
              >
                创建
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowCreate(false)
                  setNewCollectionName('')
                  setNewCollectionDesc('')
                }}
              >
                取消
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* 集合网格 */}
      {collections && collections.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {collections.map((collection) => (
            <Card
              key={collection.id}
              className="group transition-all hover:shadow-md"
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-primary/10 p-2">
                      <FolderOpen className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{collection.name}</CardTitle>
                      <CardDescription className="line-clamp-2">
                        {collection.description || '暂无描述'}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {/* 统计信息 */}
                  <div className="flex items-center justify-between rounded-lg bg-muted p-3">
                    <div className="flex items-center gap-2 text-sm">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{collection.document_count}</span>
                      <span className="text-muted-foreground">个文档</span>
                    </div>
                  </div>

                  {/* 时间信息 */}
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Calendar className="h-3 w-3" />
                    创建于 {formatRelativeTime(collection.created_at)}
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex gap-2 opacity-0 transition-opacity group-hover:opacity-100">
                    <Button variant="outline" size="sm" className="flex-1">
                      查看文档
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(collection.id, collection.name)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <FolderOpen className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
          <h3 className="mb-2 text-lg font-semibold">暂无集合</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            创建您的第一个集合来组织文档
          </p>
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="mr-2 h-4 w-4" />
            创建集合
          </Button>
        </Card>
      )}
    </div>
  )
}
