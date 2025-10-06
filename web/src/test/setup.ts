import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

// 每个测试后自动清理
afterEach(() => {
  cleanup()
})

// 扩展全局匹配器
expect.extend({})
