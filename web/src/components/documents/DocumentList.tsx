import { useState } from 'react'
import { Search, Filter, SortAsc, Trash2 } from 'lucide-react'
import { DocumentCard } from './DocumentCard'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Loading } from '@/components/common/Loading'
import type { Document } from '@/types'
import { debounce } from '@/lib/utils'

interface DocumentListProps {
  documents: Document[]
  loading?: boolean
  onView?: (document: Document) => void
  onDelete?: (document: Document) => void
  onBulkDelete?: (documents: Document[]) => void
}

export function DocumentList({
  documents,
  loading,
  onView,
  onDelete,
  onBulkDelete,
}: DocumentListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set())
  const [sortBy, setSortBy] = useState<'name' | 'date'>('date')

  // 搜索和排序
  const filteredDocuments = documents
    .filter((doc) =>
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.content?.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'name') {
        return a.filename.localeCompare(b.filename)
      }
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })

  const handleSearch = debounce((value: string) => {
    setSearchQuery(value)
  }, 300)

  const toggleSelectDoc = (docId: string) => {
    const newSelected = new Set(selectedDocs)
    if (newSelected.has(docId)) {
      newSelected.delete(docId)
    } else {
      newSelected.add(docId)
    }
    setSelectedDocs(newSelected)
  }

  const handleBulkDelete = () => {
    const docsToDelete = documents.filter((doc) => selectedDocs.has(doc.id))
    onBulkDelete?.(docsToDelete)
    setSelectedDocs(new Set())
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loading text="加载文档中..." />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 工具栏 */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        {/* 搜索框 */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="搜索文档..."
            className="pl-10"
            onChange={(e) => handleSearch(e.target.value)}
          />
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-2">
          {selectedDocs.size > 0 && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleBulkDelete}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              删除 ({selectedDocs.size})
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSortBy(sortBy === 'name' ? 'date' : 'name')}
          >
            <SortAsc className="mr-2 h-4 w-4" />
            {sortBy === 'name' ? '按名称' : '按日期'}
          </Button>
          <Button variant="outline" size="sm">
            <Filter className="mr-2 h-4 w-4" />
            筛选
          </Button>
        </div>
      </div>

      {/* 文档网格 */}
      {filteredDocuments.length === 0 ? (
        <div className="flex h-64 flex-col items-center justify-center text-muted-foreground">
          <Search className="mb-4 h-12 w-12" />
          <p>没有找到文档</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map((doc) => (
            <div
              key={doc.id}
              className="relative"
              onClick={() => toggleSelectDoc(doc.id)}
            >
              {selectedDocs.has(doc.id) && (
                <div className="absolute inset-0 z-10 rounded-lg border-2 border-primary bg-primary/10" />
              )}
              <DocumentCard
                document={doc}
                onView={onView}
                onDelete={onDelete}
              />
            </div>
          ))}
        </div>
      )}

      {/* 分页 */}
      {filteredDocuments.length > 0 && (
        <div className="flex items-center justify-between border-t pt-4">
          <p className="text-sm text-muted-foreground">
            显示 {filteredDocuments.length} 个文档
          </p>
          {/* 这里可以添加分页组件 */}
        </div>
      )}
    </div>
  )
}
