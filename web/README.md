# RAG 文档处理系统 - 前端界面

一个现代化、用户友好的 RAG（检索增强生成）文档处理系统前端界面，使用 React + TypeScript + TailwindCSS 构建。

## ✨ 功能特性

### 📊 仪表板
- 系统概览统计（文档数量、集合数量、存储大小、向量数量）
- 最近上传的文档展示
- 快速操作入口
- 使用提示和指南

### 📄 文档管理
- 拖放上传文档（支持 PDF、DOC、DOCX、TXT、MD）
- 从 URL 导入文档
- 文档列表展示（网格/列表视图）
- 搜索和筛选文档
- 批量操作（删除、导出）
- 文档详情查看

### 🔍 语义搜索
- 智能语义搜索（基于 RAG 技术）
- 高级搜索选项（集合选择、结果数量调整）
- 搜索结果高亮显示
- 相关度评分展示
- 快捷键支持（⌘K）

### 📁 集合管理
- 创建和管理文档集合
- 集合统计信息
- 集合内文档查看
- 删除集合

### 🎨 UI/UX 特性
- 响应式设计（支持移动端）
- 暗色/亮色主题切换
- 平滑动画过渡
- 直观的导航
- 实时反馈提示

## 🛠️ 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS
- **UI 组件**: Radix UI
- **状态管理**: Zustand
- **数据获取**: TanStack Query (React Query)
- **路由**: React Router v6
- **图标**: Lucide React
- **文件上传**: React Dropzone
- **通知**: React Hot Toast
- **动画**: Framer Motion

## 📦 项目结构

\`\`\`
web/
├── index.html                 # HTML 入口文件
├── package.json              # 项目依赖
├── tsconfig.json             # TypeScript 配置
├── vite.config.ts            # Vite 配置
├── tailwind.config.js        # TailwindCSS 配置
├── postcss.config.js         # PostCSS 配置
├── .eslintrc.cjs             # ESLint 配置
├── .env                      # 环境变量
└── src/
    ├── main.tsx              # 应用入口
    ├── App.tsx               # 根组件
    ├── index.css             # 全局样式
    ├── components/           # 组件目录
    │   ├── layout/          # 布局组件
    │   │   ├── Header.tsx
    │   │   ├── Sidebar.tsx
    │   │   └── Layout.tsx
    │   ├── documents/       # 文档相关组件
    │   │   ├── DocumentList.tsx
    │   │   ├── DocumentCard.tsx
    │   │   └── DocumentUpload.tsx
    │   ├── search/          # 搜索相关组件
    │   │   ├── SearchBar.tsx
    │   │   └── SearchResults.tsx
    │   └── common/          # 通用组件
    │       ├── Button.tsx
    │       ├── Input.tsx
    │       ├── Card.tsx
    │       └── Loading.tsx
    ├── pages/               # 页面组件
    │   ├── Dashboard.tsx
    │   ├── Documents.tsx
    │   ├── Search.tsx
    │   └── Collections.tsx
    ├── services/            # API 服务
    │   └── api.ts
    ├── hooks/               # 自定义 Hooks
    │   ├── useTheme.ts
    │   ├── useDocuments.ts
    │   └── useSearch.ts
    ├── store/               # 状态管理
    │   └── index.ts
    ├── types/               # 类型定义
    │   └── index.ts
    ├── lib/                 # 工具函数
    │   └── utils.ts
    └── utils/               # 辅助工具
        └── helpers.ts
\`\`\`

## 🚀 快速开始

### 前置要求

- Node.js >= 18.0.0
- npm >= 9.0.0 或 yarn >= 1.22.0

### 安装依赖

\`\`\`bash
cd web
npm install
\`\`\`

### 配置环境变量

复制 \`.env.example\` 并重命名为 \`.env\`，然后配置 API 地址：

\`\`\`env
VITE_API_BASE_URL=http://localhost:8000/api/v1
\`\`\`

### 启动开发服务器

\`\`\`bash
npm run dev
\`\`\`

应用将在 http://localhost:3000 启动。

### 构建生产版本

\`\`\`bash
npm run build
\`\`\`

构建产物将生成在 \`dist\` 目录。

### 预览生产构建

\`\`\`bash
npm run preview
\`\`\`

## 📝 可用脚本

- \`npm run dev\` - 启动开发服务器
- \`npm run build\` - 构建生产版本
- \`npm run preview\` - 预览生产构建
- \`npm run lint\` - 运行 ESLint 检查
- \`npm run type-check\` - TypeScript 类型检查

## 🔌 API 集成

前端通过以下 API 端点与后端通信：

### 文档相关
- \`POST /api/v1/documents/upload\` - 上传文档
- \`POST /api/v1/documents/from-url\` - 从 URL 导入
- \`GET /api/v1/documents\` - 获取文档列表
- \`GET /api/v1/documents/{doc_id}\` - 获取文档详情
- \`DELETE /api/v1/documents/{doc_id}\` - 删除文档
- \`POST /api/v1/documents/bulk-delete\` - 批量删除

### 搜索相关
- \`POST /api/v1/search\` - 语义搜索
- \`GET /api/v1/search/suggestions\` - 搜索建议

### 集合相关
- \`GET /api/v1/collections\` - 获取集合列表
- \`POST /api/v1/collections\` - 创建集合
- \`GET /api/v1/collections/{id}\` - 获取集合详情
- \`DELETE /api/v1/collections/{id}\` - 删除集合
- \`GET /api/v1/collections/{id}/documents\` - 获取集合文档

### 统计相关
- \`GET /api/v1/stats\` - 获取系统统计

## 🎨 主题定制

系统支持亮色/暗色主题切换，主题配置在 \`tailwind.config.js\` 和 \`src/index.css\` 中定义。

### 修改主题颜色

编辑 \`src/index.css\` 中的 CSS 变量：

\`\`\`css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96.1%;
  /* ... 其他颜色变量 */
}
\`\`\`

## 🔐 安全性

- JWT token 自动管理
- XSS 防护
- CSRF 保护
- 安全的文件上传验证
- 环境变量隔离

## ♿ 无障碍访问

- 语义化 HTML
- ARIA 属性支持
- 键盘导航
- 屏幕阅读器优化
- 颜色对比度符合 WCAG 2.1 AA 标准

## 📱 响应式设计

支持以下设备尺寸：
- 移动端：< 768px
- 平板：768px - 1024px
- 桌面：> 1024px

## 🎯 性能优化

- 代码分割和懒加载
- 图片优化
- 防抖和节流
- React Query 缓存
- 虚拟滚动（大列表）

## 🐛 调试

开发环境下可以使用 React DevTools 和 TanStack Query DevTools：

\`\`\`typescript
// 在 App.tsx 中添加
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
\`\`\`

## 📄 类型定义

所有类型定义在 \`src/types/index.ts\` 中，包括：
- Document
- SearchRequest/Response
- Collection
- SystemStats
- API Response 类型

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (\`git checkout -b feature/AmazingFeature\`)
3. 提交更改 (\`git commit -m 'Add some AmazingFeature'\`)
4. 推送到分支 (\`git push origin feature/AmazingFeature\`)
5. 开启 Pull Request

## 📜 许可证

MIT License

## 👨‍💻 开发者

RAG 文档处理系统团队

## 🙏 致谢

- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [TailwindCSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)
- [TanStack Query](https://tanstack.com/query)
- [Zustand](https://github.com/pmndrs/zustand)

## 📞 支持

如有问题或建议，请提交 Issue 或联系开发团队。

---

**享受使用 RAG 文档处理系统！** 🚀
