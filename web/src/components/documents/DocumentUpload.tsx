import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, Link as LinkIcon, Loader2 } from 'lucide-react'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Card } from '@/components/common/Card'
import { documentAPI } from '@/services/api'
import toast from 'react-hot-toast'
import { cn } from '@/lib/utils'

interface DocumentUploadProps {
  collectionId?: string
  onUploadSuccess?: () => void
}

export function DocumentUpload({ collectionId, onUploadSuccess }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const [urlInput, setUrlInput] = useState('')
  const [uploadMode, setUploadMode] = useState<'file' | 'url'>('file')

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
  })

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleUploadFiles = async () => {
    if (files.length === 0) {
      toast.error('请选择要上传的文件')
      return
    }

    setUploading(true)
    let successCount = 0
    let failCount = 0

    for (const file of files) {
      try {
        await documentAPI.upload(file, collectionId)
        successCount++
      } catch (error) {
        console.error('Upload failed:', error)
        failCount++
      }
    }

    setUploading(false)
    setFiles([])

    if (successCount > 0) {
      toast.success(`成功上传 ${successCount} 个文件`)
      onUploadSuccess?.()
    }

    if (failCount > 0) {
      toast.error(`${failCount} 个文件上传失败`)
    }
  }

  const handleUploadFromUrl = async () => {
    if (!urlInput.trim()) {
      toast.error('请输入URL')
      return
    }

    setUploading(true)

    try {
      await documentAPI.uploadFromUrl(urlInput, collectionId)
      toast.success('从URL导入成功')
      setUrlInput('')
      onUploadSuccess?.()
    } catch (error) {
      console.error('Upload from URL failed:', error)
      toast.error('从URL导入失败')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Card className="p-6">
      {/* 上传模式切换 */}
      <div className="mb-4 flex gap-2">
        <Button
          variant={uploadMode === 'file' ? 'default' : 'outline'}
          onClick={() => setUploadMode('file')}
          className="flex-1"
        >
          <Upload className="mr-2 h-4 w-4" />
          文件上传
        </Button>
        <Button
          variant={uploadMode === 'url' ? 'default' : 'outline'}
          onClick={() => setUploadMode('url')}
          className="flex-1"
        >
          <LinkIcon className="mr-2 h-4 w-4" />
          URL导入
        </Button>
      </div>

      {/* 文件上传模式 */}
      {uploadMode === 'file' && (
        <>
          <div
            {...getRootProps()}
            className={cn(
              'cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors',
              isDragActive
                ? 'border-primary bg-primary/5'
                : 'border-muted-foreground/25 hover:border-muted-foreground/50'
            )}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
            <p className="mt-4 text-sm font-medium">
              {isDragActive ? '释放以上传文件' : '拖放文件到此处，或点击选择文件'}
            </p>
            <p className="mt-2 text-xs text-muted-foreground">
              支持 PDF, DOC, DOCX, TXT, MD 格式
            </p>
          </div>

          {/* 文件列表 */}
          {files.length > 0 && (
            <div className="mt-4 space-y-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex items-center gap-3">
                    <File className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">{file.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(index)}
                    disabled={uploading}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* 上传按钮 */}
          {files.length > 0 && (
            <Button
              className="mt-4 w-full"
              onClick={handleUploadFiles}
              disabled={uploading}
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  上传中...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  上传 {files.length} 个文件
                </>
              )}
            </Button>
          )}
        </>
      )}

      {/* URL导入模式 */}
      {uploadMode === 'url' && (
        <div className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium">文档URL</label>
            <Input
              type="url"
              placeholder="https://example.com/document.pdf"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              disabled={uploading}
            />
          </div>
          <Button
            className="w-full"
            onClick={handleUploadFromUrl}
            disabled={uploading || !urlInput.trim()}
          >
            {uploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                导入中...
              </>
            ) : (
              <>
                <LinkIcon className="mr-2 h-4 w-4" />
                从URL导入
              </>
            )}
          </Button>
        </div>
      )}
    </Card>
  )
}
