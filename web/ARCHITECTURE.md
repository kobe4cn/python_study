# 项目架构说明

## 🏗️ 整体架构

本项目采用现代化的前端架构，基于组件化、类型安全和性能优化的原则设计。

```
┌─────────────────────────────────────────────┐
│            用户界面层 (UI Layer)              │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Pages  │  │ Components│  │ Layouts  │   │
│  └─────────┘  └──────────┘  └──────────┘   │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│          业务逻辑层 (Logic Layer)             │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Hooks  │  │  Store   │  │  Utils   │   │
│  └─────────┘  └──────────┘  └──────────┘   │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│          数据层 (Data Layer)                 │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API   │  │  Query   │  │  Types   │   │
│  └─────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────┘
```

## 📁 目录结构详解

### `/src/components` - 组件目录

#### `layout/` - 布局组件
- **Header.tsx**: 顶部导航栏
  - Logo 和品牌展示
  - 全局搜索框
  - 主题切换按钮
  - 用户菜单

- **Sidebar.tsx**: 侧边导航栏
  - 主导航菜单
  - 移动端响应式抽屉
  - 活动状态指示

- **Layout.tsx**: 页面布局容器
  - 组合 Header 和 Sidebar
  - 路由出口 (Outlet)
  - Toast 通知容器

#### `documents/` - 文档管理组件
- **DocumentUpload.tsx**: 文档上传组件
  - 拖放上传
  - URL 导入
  - 批量上传
  - 上传进度显示

- **DocumentCard.tsx**: 文档卡片
  - 文档信息展示
  - 快捷操作按钮
  - 元数据标签

- **DocumentList.tsx**: 文档列表
  - 网格/列表视图
  - 搜索和筛选
  - 排序功能
  - 批量选择

#### `search/` - 搜索组件
- **SearchBar.tsx**: 搜索栏
  - 实时搜索
  - 高级选项
  - 快捷键支持
  - 搜索建议

- **SearchResults.tsx**: 搜索结果
  - 结果列表
  - 相关度评分
  - 关键词高亮
  - 分页

#### `common/` - 通用组件
基于 Radix UI 构建的可复用组件：
- Button, Input, Card
- Loading, Modal, Toast
- Select, Switch, Tabs

### `/src/pages` - 页面组件

- **Dashboard.tsx**: 仪表板
  - 系统统计概览
  - 快速操作入口
  - 最近文档展示

- **Documents.tsx**: 文档管理页
  - 文档列表
  - 上传功能
  - 批量操作

- **Search.tsx**: 搜索页
  - 语义搜索
  - 高级筛选
  - 结果展示

- **Collections.tsx**: 集合管理页
  - 集合列表
  - 创建/编辑集合
  - 集合统计

### `/src/services` - API 服务层

**api.ts** - 统一的 API 接口封装
```typescript
// Axios 实例配置
- 基础 URL 配置
- 请求/响应拦截器
- 错误统一处理
- Token 自动注入

// API 模块
documentAPI    // 文档相关 API
searchAPI      // 搜索相关 API
collectionAPI  // 集合相关 API
statsAPI       // 统计相关 API
```

### `/src/hooks` - 自定义 Hooks

- **useTheme.ts**: 主题管理
  - 主题切换
  - 持久化存储
  - DOM 类名同步

- **useDocuments.ts**: 文档操作
  - 文档列表查询
  - 上传/删除操作
  - 缓存管理

- **useSearch.ts**: 搜索功能
  - 搜索执行
  - 结果管理
  - 加载状态

### `/src/store` - 状态管理

使用 Zustand 进行全局状态管理：
```typescript
// 应用状态
- theme: 主题设置
- user: 用户信息（未来扩展）
- settings: 系统设置（未来扩展）
```

### `/src/types` - 类型定义

完整的 TypeScript 类型系统：
- Document: 文档数据模型
- SearchRequest/Response: 搜索相关类型
- Collection: 集合数据模型
- API 通用类型

### `/src/lib` - 工具库

**utils.ts** - 通用工具函数
- `cn()`: 类名合并
- `formatFileSize()`: 文件大小格式化
- `formatDate()`: 日期格式化
- `debounce()`: 防抖
- `throttle()`: 节流
- `highlightText()`: 文本高亮

## 🔄 数据流

### 1. 用户操作流程
```
用户交互 → 组件事件 → Hook/Store → API 调用 → 后端
                                    ↓
用户界面 ← 组件更新 ← React Query 缓存 ← API 响应
```

### 2. React Query 缓存策略
```typescript
// 默认配置
{
  staleTime: 5分钟,     // 数据新鲜度
  cacheTime: 10分钟,    // 缓存时间
  refetchOnWindowFocus: false,  // 窗口聚焦不重新获取
  retry: 1              // 失败重试1次
}
```

### 3. 状态管理层级
```
Local State (useState)          // 组件内部状态
      ↓
Server State (React Query)      // 服务器数据缓存
      ↓
Global State (Zustand)          // 全局应用状态
```

## 🎨 设计系统

### 颜色变量
基于 HSL 色彩空间，支持亮色/暗色主题：
```css
--primary: 主色调
--secondary: 辅助色
--accent: 强调色
--destructive: 危险操作色
--muted: 柔和色
```

### 组件规范
- 所有组件使用 TypeScript
- Props 接口明确定义
- 支持 className 覆盖
- 使用 forwardRef 传递引用

### 响应式断点
```typescript
sm: 640px   // 小屏幕
md: 768px   // 中等屏幕
lg: 1024px  // 大屏幕
xl: 1280px  // 超大屏幕
```

## 🔐 安全机制

### 1. XSS 防护
- React 自动转义
- DOMPurify 清理用户输入（如需要）
- Content Security Policy

### 2. CSRF 防护
- Token 验证
- SameSite Cookie

### 3. API 安全
- JWT Token 管理
- 请求签名
- 敏感数据加密

## ⚡ 性能优化

### 1. 代码分割
```typescript
// 路由级别懒加载
const Dashboard = lazy(() => import('./pages/Dashboard'))
```

### 2. 图片优化
- 懒加载
- WebP 格式
- 响应式图片

### 3. 渲染优化
- React.memo 避免重渲染
- useMemo/useCallback 缓存计算
- 虚拟滚动大列表

### 4. 网络优化
- React Query 自动缓存
- 请求防抖/节流
- 预加载关键资源

## 🧪 测试策略

### 单元测试
- 工具函数测试
- Hook 测试
- 组件单元测试

### 集成测试
- API 集成测试
- 用户流程测试

### E2E 测试
- 关键业务流程
- 跨浏览器测试

## 📦 构建优化

### Vite 配置优化
```typescript
{
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['@radix-ui/*'],
        }
      }
    }
  }
}
```

### Tree Shaking
- ES Module 导入
- 只导入需要的组件
- 移除未使用代码

## 🔄 未来扩展

### 计划功能
1. **用户系统**
   - 登录/注册
   - 权限管理
   - 用户配置

2. **协作功能**
   - 文档分享
   - 评论系统
   - 实时协作

3. **高级搜索**
   - 过滤器保存
   - 搜索历史
   - 智能推荐

4. **数据可视化**
   - 文档关系图
   - 使用统计图表
   - 趋势分析

### 扩展建议
- 添加 i18n 国际化
- 集成分析工具
- PWA 支持
- WebSocket 实时更新

## 📚 技术决策记录

### 为什么选择 Vite？
- 极快的开发服务器启动
- HMR 热更新
- 优化的生产构建

### 为什么选择 React Query？
- 自动缓存管理
- 后台数据同步
- 乐观更新支持

### 为什么选择 Zustand？
- 轻量级（3KB）
- 无样板代码
- TypeScript 友好

### 为什么选择 TailwindCSS？
- 原子化 CSS
- 高度可定制
- 优秀的 DX

## 🤝 贡献指南

### 代码规范
- ESLint + Prettier
- TypeScript 严格模式
- 组件命名：PascalCase
- 文件命名：kebab-case

### Git 工作流
- main: 生产分支
- develop: 开发分支
- feature/*: 功能分支
- fix/*: 修复分支

### Commit 规范
```
feat: 新功能
fix: 修复
docs: 文档
style: 格式
refactor: 重构
test: 测试
chore: 构建/工具
```

---

**持续更新中...** 如有问题，请查阅源码或提交 Issue。
