import { File, Calendar, Trash2, Eye, MoreVertical } from 'lucide-react'
import { Card, CardContent } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import type { Document } from '@/types'
import { formatFileSize, formatRelativeTime, getFileExtension, getFileTypeColor } from '@/lib/utils'

interface DocumentCardProps {
  document: Document
  onView?: (document: Document) => void
  onDelete?: (document: Document) => void
}

export function DocumentCard({ document, onView, onDelete }: DocumentCardProps) {
  const extension = getFileExtension(document.filename)
  const fileTypeColor = getFileTypeColor(extension)

  return (
    <Card className="group transition-all hover:shadow-md">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          {/* 文件信息 */}
          <div className="flex flex-1 items-start gap-3">
            <div className={`rounded-lg bg-muted p-2 ${fileTypeColor}`}>
              <File className="h-6 w-6" />
            </div>
            <div className="flex-1 space-y-1">
              <h3 className="font-medium line-clamp-1" title={document.filename}>
                {document.filename}
              </h3>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {formatRelativeTime(document.created_at)}
                </span>
                {document.file_size && (
                  <span>{formatFileSize(document.file_size)}</span>
                )}
                {extension && (
                  <span className="uppercase">{extension}</span>
                )}
              </div>
              {document.content && (
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {document.content.substring(0, 150)}...
                </p>
              )}
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            {onView && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onView(document)}
                title="查看详情"
              >
                <Eye className="h-4 w-4" />
              </Button>
            )}
            {onDelete && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onDelete(document)}
                title="删除文档"
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            )}
            <Button variant="ghost" size="icon" title="更多操作">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* 元数据标签 */}
        {document.metadata && Object.keys(document.metadata).length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {Object.entries(document.metadata).slice(0, 3).map(([key, value]) => (
              <span
                key={key}
                className="rounded-full bg-secondary px-2 py-1 text-xs text-secondary-foreground"
              >
                {key}: {String(value)}
              </span>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
