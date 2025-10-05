import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { DocumentList } from '@/components/documents/DocumentList'
import { DocumentUpload } from '@/components/documents/DocumentUpload'
import { Button } from '@/components/common/Button'
import { documentAPI } from '@/services/api'
import type { Document } from '@/types'
import toast from 'react-hot-toast'

export function Documents() {
  const [showUpload, setShowUpload] = useState(false)
  const queryClient = useQueryClient()

  // 获取文档列表
  const { data, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentAPI.list(),
  })

  // 删除文档
  const deleteMutation = useMutation({
    mutationFn: (documentId: string) => documentAPI.delete(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      toast.success('文档删除成功')
    },
    onError: () => {
      toast.error('文档删除失败')
    },
  })

  // 批量删除
  const bulkDeleteMutation = useMutation({
    mutationFn: (documentIds: string[]) => documentAPI.bulkDelete(documentIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      toast.success('批量删除成功')
    },
    onError: () => {
      toast.error('批量删除失败')
    },
  })

  const handleDelete = (document: Document) => {
    if (window.confirm(`确定要删除文档 "${document.filename}" 吗？`)) {
      deleteMutation.mutate(document.id)
    }
  }

  const handleBulkDelete = (documents: Document[]) => {
    if (window.confirm(`确定要删除选中的 ${documents.length} 个文档吗？`)) {
      bulkDeleteMutation.mutate(documents.map((doc) => doc.id))
    }
  }

  const handleUploadSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['documents'] })
    setShowUpload(false)
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">文档管理</h1>
          <p className="text-muted-foreground">
            上传、管理和组织您的文档
          </p>
        </div>
        <Button onClick={() => setShowUpload(!showUpload)}>
          <Plus className="mr-2 h-4 w-4" />
          {showUpload ? '隐藏上传' : '上传文档'}
        </Button>
      </div>

      {/* 上传区域 */}
      {showUpload && (
        <DocumentUpload onUploadSuccess={handleUploadSuccess} />
      )}

      {/* 文档列表 */}
      <DocumentList
        documents={data?.items || []}
        loading={isLoading}
        onDelete={handleDelete}
        onBulkDelete={handleBulkDelete}
      />
    </div>
  )
}
