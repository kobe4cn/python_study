import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { SearchBar } from '@/components/search/SearchBar'
import { SearchResults } from '@/components/search/SearchResults'
import { Card } from '@/components/common/Card'
import { searchAPI, collectionAPI } from '@/services/api'
import type { SearchRequest, SearchResponse } from '@/types'

export function Search() {
  const [searchRequest, setSearchRequest] = useState<SearchRequest | null>(null)
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null)

  // 获取集合列表
  const { data: collections } = useQuery({
    queryKey: ['collections'],
    queryFn: collectionAPI.list,
  })

  // 执行搜索
  const { data: searchData, isLoading } = useQuery<SearchResponse>({
    queryKey: ['search', searchRequest],
    queryFn: () => searchAPI.search(searchRequest!),
    enabled: !!searchRequest,
  })

  // React Query v5: 使用 useEffect 替代 onSuccess
  useEffect(() => {
    if (searchData) {
      setSearchResponse(searchData)
    }
  }, [searchData])

  const handleSearch = (request: SearchRequest) => {
    setSearchRequest(request)
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">语义搜索</h1>
        <p className="text-muted-foreground">
          使用 RAG 技术进行智能文档检索
        </p>
      </div>

      {/* 搜索框 */}
      <SearchBar
        onSearch={handleSearch}
        loading={isLoading}
        collections={collections?.map((c) => ({ id: c.id, name: c.name }))}
      />

      {/* 搜索结果 */}
      {searchResponse && (
        <div>
          <h2 className="mb-4 text-xl font-semibold">
            搜索结果 "{searchResponse.query}"
          </h2>
          <SearchResults
            results={searchResponse.results}
            query={searchResponse.query}
            executionTime={searchResponse.execution_time}
          />
        </div>
      )}

      {/* 搜索说明 */}
      {!searchResponse && (
        <Card className="p-8 text-center">
          <div className="mx-auto max-w-md space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
              <svg
                className="h-8 w-8 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold">开始搜索</h3>
            <p className="text-sm text-muted-foreground">
              输入关键词或问题，系统将使用语义搜索技术为您找到最相关的文档内容。
              支持自然语言查询，无需精确匹配关键词。
            </p>
            <div className="mt-6 space-y-2 text-left text-sm">
              <p className="font-medium">搜索技巧：</p>
              <ul className="space-y-1 text-muted-foreground">
                <li>• 使用完整的句子或问题进行搜索</li>
                <li>• 选择特定集合可以缩小搜索范围</li>
                <li>• 调整返回结果数量以获取更多或更少的匹配</li>
                <li>• 搜索结果按相关度评分排序</li>
              </ul>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
