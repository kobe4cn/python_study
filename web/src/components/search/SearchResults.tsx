import { FileText, Star, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card'
import type { SearchResult } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

interface SearchResultsProps {
  results: SearchResult[]
  query: string
  executionTime?: number
}

export function SearchResults({ results, query, executionTime }: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-muted-foreground">
        <FileText className="mb-4 h-12 w-12" />
        <p className="text-lg font-medium">未找到相关结果</p>
        <p className="text-sm">尝试使用不同的关键词进行搜索</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 搜索统计 */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <p>
          找到 <span className="font-semibold text-foreground">{results.length}</span> 个相关结果
        </p>
        {executionTime && (
          <p className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {executionTime.toFixed(2)}秒
          </p>
        )}
      </div>

      {/* 结果列表 */}
      <div className="space-y-3">
        {results.map((result, index) => (
          <Card
            key={result.id}
            className="transition-all hover:shadow-md"
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                    {index + 1}
                  </span>
                  <CardTitle className="text-base">
                    文档片段 {result.document_id.substring(0, 8)}...
                  </CardTitle>
                </div>
                <div className="flex items-center gap-1 rounded-full bg-yellow-100 px-2 py-1 text-xs font-semibold text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
                  <Star className="h-3 w-3 fill-current" />
                  {(result.score * 100).toFixed(1)}%
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* 内容预览 */}
              <div className="mb-3 rounded-lg bg-muted p-4">
                <p className="text-sm leading-relaxed">
                  {highlightQuery(result.content, query)}
                </p>
              </div>

              {/* 元数据 */}
              <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
                {result.metadata?.source && (
                  <span>来源: {result.metadata.source}</span>
                )}
                {result.metadata?.created_date && (
                  <span>
                    创建: {formatRelativeTime(result.metadata.created_date)}
                  </span>
                )}
                {result.metadata?.page_count && (
                  <span>页数: {result.metadata.page_count}</span>
                )}
              </div>

              {/* 高亮片段 */}
              {result.highlights && result.highlights.length > 0 && (
                <div className="mt-3 border-l-2 border-primary pl-4">
                  {result.highlights.map((highlight, i) => (
                    <p key={i} className="text-xs text-muted-foreground">
                      {highlight}
                    </p>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// 高亮关键词
function highlightQuery(text: string, query: string): React.ReactNode {
  if (!query) return text

  const parts = text.split(new RegExp(`(${query})`, 'gi'))
  return parts.map((part, index) =>
    part.toLowerCase() === query.toLowerCase() ? (
      <mark
        key={index}
        className="bg-yellow-200 font-semibold text-yellow-900 dark:bg-yellow-900/50 dark:text-yellow-200"
      >
        {part}
      </mark>
    ) : (
      part
    )
  )
}
