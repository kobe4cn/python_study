import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { searchAPI } from '@/services/api'
import type { SearchRequest, SearchResponse } from '@/types'
import toast from 'react-hot-toast'

export function useSearch() {
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null)

  const searchMutation = useMutation({
    mutationFn: (request: SearchRequest) => searchAPI.search(request),
    onSuccess: (data) => {
      setSearchResults(data)
      if (data.results.length === 0) {
        toast('未找到相关结果', { icon: '🔍' })
      }
    },
    onError: (error) => {
      console.error('Search failed:', error)
      toast.error('搜索失败，请重试')
    },
  })

  const search = (request: SearchRequest) => {
    searchMutation.mutate(request)
  }

  const clearResults = () => {
    setSearchResults(null)
  }

  return {
    search,
    searchResults,
    clearResults,
    isSearching: searchMutation.isPending,
    error: searchMutation.error,
  }
}
