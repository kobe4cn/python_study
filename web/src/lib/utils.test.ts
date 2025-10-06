import { describe, it, expect, vi } from 'vitest'
import {
  cn,
  formatFileSize,
  formatDate,
  truncate,
  debounce,
  isValidUrl,
  getFileExtension,
  getFileTypeColor,
} from './utils'

describe('Utils Library', () => {
  describe('cn', () => {
    it('merges class names correctly', () => {
      expect(cn('px-4', 'py-2')).toBe('px-4 py-2')
    })

    it('handles conditional classes', () => {
      expect(cn('base', false && 'hidden', true && 'visible')).toBe('base visible')
    })

    it('resolves Tailwind conflicts', () => {
      expect(cn('px-2', 'px-4')).toBe('px-4')
    })
  })

  describe('formatFileSize', () => {
    it('formats bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes')
      expect(formatFileSize(1024)).toBe('1 KB')
      expect(formatFileSize(1048576)).toBe('1 MB')
      expect(formatFileSize(1073741824)).toBe('1 GB')
    })

    it('rounds to 2 decimal places', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB')
    })
  })

  describe('formatDate', () => {
    it('formats date strings', () => {
      const date = new Date('2024-01-15T10:30:00')
      const formatted = formatDate(date)
      expect(formatted).toMatch(/2024/)
      expect(formatted).toMatch(/01/)
      expect(formatted).toMatch(/15/)
    })

    it('accepts Date objects', () => {
      const date = new Date('2024-01-15')
      expect(formatDate(date)).toBeTruthy()
    })
  })

  describe('truncate', () => {
    it('truncates long text', () => {
      expect(truncate('Hello World', 5)).toBe('Hello...')
    })

    it('does not truncate short text', () => {
      expect(truncate('Hi', 5)).toBe('Hi')
    })

    it('handles exact length', () => {
      expect(truncate('Hello', 5)).toBe('Hello')
    })
  })

  describe('debounce', () => {
    it('delays function execution', async () => {
      const func = vi.fn()
      const debounced = debounce(func, 100)

      debounced()
      expect(func).not.toHaveBeenCalled()

      await new Promise((resolve) => setTimeout(resolve, 150))
      expect(func).toHaveBeenCalledTimes(1)
    })

    it('cancels previous calls', async () => {
      const func = vi.fn()
      const debounced = debounce(func, 100)

      debounced()
      debounced()
      debounced()

      await new Promise((resolve) => setTimeout(resolve, 150))
      expect(func).toHaveBeenCalledTimes(1)
    })
  })

  describe('isValidUrl', () => {
    it('validates correct URLs', () => {
      expect(isValidUrl('https://example.com')).toBe(true)
      expect(isValidUrl('http://localhost:3000')).toBe(true)
    })

    it('rejects invalid URLs', () => {
      expect(isValidUrl('not a url')).toBe(false)
      expect(isValidUrl('example.com')).toBe(false)
    })
  })

  describe('getFileExtension', () => {
    it('extracts file extensions', () => {
      expect(getFileExtension('document.pdf')).toBe('pdf')
      expect(getFileExtension('image.png')).toBe('png')
      expect(getFileExtension('archive.tar.gz')).toBe('gz')
    })

    it('handles files without extensions', () => {
      expect(getFileExtension('README')).toBe('')
    })
  })

  describe('getFileTypeColor', () => {
    it('returns colors for known types', () => {
      expect(getFileTypeColor('pdf')).toBe('text-red-500')
      expect(getFileTypeColor('doc')).toBe('text-blue-500')
      expect(getFileTypeColor('md')).toBe('text-purple-500')
    })

    it('returns default color for unknown types', () => {
      expect(getFileTypeColor('unknown')).toBe('text-gray-500')
    })

    it('handles uppercase extensions', () => {
      expect(getFileTypeColor('PDF')).toBe('text-red-500')
    })
  })
})
