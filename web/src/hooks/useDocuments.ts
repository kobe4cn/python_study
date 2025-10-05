import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentAPI } from '@/services/api'
import toast from 'react-hot-toast'

export function useDocuments() {
  const queryClient = useQueryClient()

  const {
    data: documents,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentAPI.list(),
  })

  const uploadMutation = useMutation({
    mutationFn: ({
      file,
      collectionId,
      metadata,
    }: {
      file: File
      collectionId?: string
      metadata?: Record<string, any>
    }) => documentAPI.upload(file, collectionId, metadata),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      toast.success('文档上传成功')
    },
    onError: (error) => {
      console.error('Upload failed:', error)
      toast.error('文档上传失败')
    },
  })

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

  return {
    documents: documents?.items || [],
    isLoading,
    error,
    uploadDocument: uploadMutation.mutate,
    deleteDocument: deleteMutation.mutate,
    isUploading: uploadMutation.isPending,
    isDeleting: deleteMutation.isPending,
  }
}
