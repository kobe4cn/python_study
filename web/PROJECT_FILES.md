# 📂 项目文件清单

## 配置文件 (Configuration Files)

### 构建和开发工具配置
- ✅ `package.json` - 项目依赖和脚本配置
- ✅ `tsconfig.json` - TypeScript 编译配置
- ✅ `tsconfig.node.json` - Node.js TypeScript 配置
- ✅ `vite.config.ts` - Vite 构建工具配置
- ✅ `tailwind.config.js` - TailwindCSS 样式配置
- ✅ `postcss.config.js` - PostCSS 配置
- ✅ `.eslintrc.cjs` - ESLint 代码检查配置

### 环境和版本控制
- ✅ `.env` - 环境变量
- ✅ `.env.example` - 环境变量示例
- ✅ `.gitignore` - Git 忽略文件配置

### HTML 入口
- ✅ `index.html` - 应用 HTML 入口文件

## 源代码文件 (Source Code)

### 应用入口 (`/src`)
- ✅ `main.tsx` - React 应用入口
- ✅ `App.tsx` - 根组件和路由配置
- ✅ `index.css` - 全局样式
- ✅ `vite-env.d.ts` - Vite 环境类型定义

### 类型定义 (`/src/types`)
- ✅ `index.ts` - 完整的 TypeScript 类型定义
  - Document 类型
  - SearchRequest/Response 类型
  - Collection 类型
  - SystemStats 类型
  - API 响应类型
  - UI 状态类型

### API 服务层 (`/src/services`)
- ✅ `api.ts` - 统一的 API 接口封装
  - Axios 实例配置
  - 请求/响应拦截器
  - documentAPI - 文档相关接口
  - searchAPI - 搜索相关接口
  - collectionAPI - 集合相关接口
  - statsAPI - 统计相关接口

### 工具函数 (`/src/lib`)
- ✅ `utils.ts` - 通用工具函数库
  - 类名合并 (cn)
  - 文件大小格式化
  - 日期格式化
  - 防抖/节流
  - 文本高亮
  - 剪贴板操作

### 状态管理 (`/src/store`)
- ✅ `index.ts` - Zustand 全局状态管理
  - 主题状态
  - 主题切换逻辑

### 自定义 Hooks (`/src/hooks`)
- ✅ `useTheme.ts` - 主题管理 Hook
- ✅ `useDocuments.ts` - 文档操作 Hook
- ✅ `useSearch.ts` - 搜索功能 Hook

## 组件文件 (Components)

### 布局组件 (`/src/components/layout`)
- ✅ `Header.tsx` - 顶部导航栏
  - Logo 和品牌
  - 全局搜索
  - 主题切换
  - 移动端菜单按钮

- ✅ `Sidebar.tsx` - 侧边导航栏
  - 导航菜单
  - 响应式抽屉
  - 活动状态指示

- ✅ `Layout.tsx` - 页面布局容器
  - 组合 Header 和 Sidebar
  - 路由出口
  - Toast 通知

### 文档管理组件 (`/src/components/documents`)
- ✅ `DocumentUpload.tsx` - 文档上传
  - 拖放上传
  - URL 导入
  - 批量上传
  - 上传进度

- ✅ `DocumentCard.tsx` - 文档卡片
  - 文档信息展示
  - 快捷操作
  - 元数据标签

- ✅ `DocumentList.tsx` - 文档列表
  - 网格视图
  - 搜索筛选
  - 排序功能
  - 批量选择

### 搜索组件 (`/src/components/search`)
- ✅ `SearchBar.tsx` - 搜索栏
  - 实时搜索
  - 高级选项
  - 快捷键支持
  - 搜索建议

- ✅ `SearchResults.tsx` - 搜索结果
  - 结果列表
  - 相关度评分
  - 关键词高亮
  - 执行时间显示

### 通用组件 (`/src/components/common`)
- ✅ `Button.tsx` - 按钮组件
  - 多种样式变体
  - 多种尺寸
  - 加载状态

- ✅ `Input.tsx` - 输入框组件
  - 统一样式
  - 表单集成

- ✅ `Card.tsx` - 卡片组件
  - Card, CardHeader, CardTitle
  - CardDescription, CardContent, CardFooter

- ✅ `Loading.tsx` - 加载组件
  - Loading 指示器
  - LoadingOverlay 遮罩

## 页面组件 (Pages)

### 主要页面 (`/src/pages`)
- ✅ `Dashboard.tsx` - 仪表板
  - 系统统计概览
  - 快速操作入口
  - 最近文档
  - 使用提示

- ✅ `Documents.tsx` - 文档管理页
  - 文档列表
  - 上传功能
  - 批量操作
  - 搜索筛选

- ✅ `Search.tsx` - 搜索页
  - 语义搜索
  - 高级筛选
  - 结果展示
  - 搜索说明

- ✅ `Collections.tsx` - 集合管理页
  - 集合列表
  - 创建集合
  - 集合统计
  - 删除集合

## 文档文件 (Documentation)

- ✅ `README.md` - 项目说明文档
  - 功能介绍
  - 技术栈说明
  - 安装和使用指南
  - API 集成说明

- ✅ `ARCHITECTURE.md` - 架构设计文档
  - 整体架构
  - 目录结构详解
  - 数据流说明
  - 设计系统
  - 性能优化

- ✅ `QUICKSTART.md` - 快速启动指南
  - 安装步骤
  - 配置说明
  - 常见问题
  - 开发脚本

- ✅ `PROJECT_FILES.md` - 项目文件清单（本文件）

## 统计信息

### 文件数量
- **配置文件**: 11 个
- **源代码文件**: 26 个
- **组件文件**: 13 个
- **页面文件**: 4 个
- **文档文件**: 4 个

### 代码行数（估计）
- TypeScript/TSX: ~3,500 行
- CSS: ~300 行
- 配置文件: ~200 行
- 文档: ~1,500 行

### 技术栈组件
- React 18
- TypeScript 5.5
- Vite 5.3
- TailwindCSS 3.4
- TanStack Query 5.51
- Zustand 4.5
- React Router 6.26
- Radix UI 组件
- Lucide React 图标

## 项目特性清单

### ✅ 已实现功能
- [x] 响应式布局
- [x] 主题切换（亮色/暗色）
- [x] 文档上传（拖放 + URL）
- [x] 文档列表和管理
- [x] 语义搜索
- [x] 集合管理
- [x] 实时搜索建议
- [x] 批量操作
- [x] 加载状态
- [x] 错误处理
- [x] Toast 通知
- [x] 快捷键支持
- [x] TypeScript 类型安全
- [x] API 缓存策略
- [x] 代码分割

### 🚧 可扩展功能
- [ ] 用户认证
- [ ] 权限管理
- [ ] 文档编辑
- [ ] 协作功能
- [ ] 国际化 (i18n)
- [ ] PWA 支持
- [ ] WebSocket 实时更新
- [ ] 数据可视化
- [ ] 导出功能
- [ ] 高级筛选器

## 依赖清单

### 核心依赖
```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "react-router-dom": "^6.26.0",
  "@tanstack/react-query": "^5.51.0",
  "zustand": "^4.5.4",
  "axios": "^1.7.3"
}
```

### UI 库
```json
{
  "tailwindcss": "^3.4.7",
  "@radix-ui/react-*": "^1.1.x",
  "lucide-react": "^0.427.0",
  "framer-motion": "^11.3.24"
}
```

### 工具库
```json
{
  "clsx": "^2.1.1",
  "tailwind-merge": "^2.5.0",
  "react-dropzone": "^14.2.3",
  "date-fns": "^3.6.0",
  "react-hot-toast": "^2.4.1"
}
```

## 浏览器兼容性

- Chrome/Edge: ≥90
- Firefox: ≥88
- Safari: ≥14
- 移动端浏览器: 现代浏览器

## 性能指标目标

- **首次内容绘制 (FCP)**: < 1.5s
- **最大内容绘制 (LCP)**: < 2.5s
- **累计布局偏移 (CLS)**: < 0.1
- **首次输入延迟 (FID)**: < 100ms
- **包大小**: < 500KB (gzipped)

---

**最后更新**: 2024-10-04
**版本**: 1.0.0
**维护者**: RAG 文档系统开发团队
