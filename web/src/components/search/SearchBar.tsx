import { useState, useRef, useEffect } from 'react'
import { Search, Loader2, Settings, X } from 'lucide-react'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import type { SearchRequest } from '@/types'

interface SearchBarProps {
  onSearch: (request: SearchRequest) => void
  loading?: boolean
  collections?: Array<{ id: string; name: string }>
}

export function SearchBar({ onSearch, loading, collections }: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [topK, setTopK] = useState(5)
  const [selectedCollection, setSelectedCollection] = useState<string>('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // 快捷键支持
    const handleKeyPress = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    onSearch({
      query: query.trim(),
      collection_id: selectedCollection || undefined,
      top_k: topK,
    })
  }

  const handleClear = () => {
    setQuery('')
    inputRef.current?.focus()
  }

  return (
    <div className="space-y-4">
      {/* 主搜索框 */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          <Input
            ref={inputRef}
            type="text"
            placeholder="输入搜索内容... (⌘K)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-14 pl-12 pr-32 text-lg"
            disabled={loading}
          />
          <div className="absolute right-2 top-1/2 flex -translate-y-1/2 gap-2">
            {query && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={handleClear}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => setShowAdvanced(!showAdvanced)}
              title="高级选项"
            >
              <Settings className="h-4 w-4" />
            </Button>
            <Button
              type="submit"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  搜索
                </>
              )}
            </Button>
          </div>
        </div>
      </form>

      {/* 高级选项 */}
      {showAdvanced && (
        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-4 font-semibold">高级搜索选项</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            {/* 集合选择 */}
            <div>
              <label className="mb-2 block text-sm font-medium">
                搜索范围
              </label>
              <select
                value={selectedCollection}
                onChange={(e) => setSelectedCollection(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="">所有集合</option>
                {collections?.map((collection) => (
                  <option key={collection.id} value={collection.id}>
                    {collection.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Top K 设置 */}
            <div>
              <label className="mb-2 block text-sm font-medium">
                返回结果数量: {topK}
              </label>
              <input
                type="range"
                min="1"
                max="20"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full"
              />
              <div className="mt-1 flex justify-between text-xs text-muted-foreground">
                <span>1</span>
                <span>20</span>
              </div>
            </div>
          </div>

          {/* 重置按钮 */}
          <div className="mt-4 flex justify-end">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSelectedCollection('')
                setTopK(5)
              }}
            >
              重置选项
            </Button>
          </div>
        </div>
      )}

      {/* 搜索提示 */}
      <div className="flex flex-wrap gap-2">
        <span className="text-sm text-muted-foreground">建议搜索:</span>
        {['机器学习', '深度学习', 'RAG技术', '向量数据库'].map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => setQuery(suggestion)}
            className="rounded-full bg-secondary px-3 py-1 text-xs hover:bg-secondary/80"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}
