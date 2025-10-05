# 🚀 快速启动指南

## 第一步：安装依赖

```bash
cd web
npm install
```

**预计时间**: 2-3 分钟

## 第二步：配置环境变量

创建 `.env` 文件（或使用已有的）：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

确保后端 API 服务器运行在 `http://localhost:8000`

## 第三步：启动开发服务器

```bash
npm run dev
```

应用将在 **http://localhost:3000** 启动

**预计时间**: 5-10 秒

## ✅ 验证安装

访问 http://localhost:3000，您应该看到：

1. ✓ 仪表板页面加载成功
2. ✓ 侧边栏导航显示
3. ✓ 主题切换按钮工作
4. ✓ 无控制台错误

## 🎯 开始使用

### 1️⃣ 上传文档

1. 点击侧边栏 **"文档管理"**
2. 点击 **"上传文档"** 按钮
3. 拖放文件或点击选择文件
4. 支持格式：PDF, DOC, DOCX, TXT, MD

### 2️⃣ 语义搜索

1. 点击侧边栏 **"语义搜索"**
2. 在搜索框输入查询内容
3. 查看搜索结果和相关度评分
4. 使用高级选项调整搜索范围

### 3️⃣ 管理集合

1. 点击侧边栏 **"集合管理"**
2. 创建新集合
3. 将文档组织到不同集合
4. 查看集合统计信息

## 🔧 常见问题

### Q: 页面显示空白？
**A**: 检查浏览器控制台是否有错误，确保所有依赖安装完成

### Q: API 请求失败？
**A**:
- 检查后端服务是否运行
- 验证 `.env` 中的 `VITE_API_BASE_URL` 配置
- 查看浏览器 Network 标签的请求详情

### Q: 主题切换不工作？
**A**: 清除浏览器 localStorage，刷新页面

### Q: 文件上传失败？
**A**:
- 检查文件格式是否支持
- 确认后端上传端点可用
- 查看文件大小是否超限

## 📱 移动端测试

在移动设备上测试：

1. 确保设备和开发机在同一网络
2. 获取开发机 IP 地址：
   ```bash
   # macOS/Linux
   ifconfig | grep inet

   # Windows
   ipconfig
   ```
3. 在移动设备浏览器访问：`http://[你的IP]:3000`

## 🛠️ 开发工具

### React DevTools
安装浏览器扩展查看组件树和 props

### TanStack Query DevTools
开发模式自动启用，查看缓存状态

### 快捷键
- `⌘K` (Mac) / `Ctrl+K` (Windows): 快速搜索
- `⌘D` (Mac) / `Ctrl+D` (Windows): 切换主题

## 🔄 下一步

- 📖 阅读 [README.md](./README.md) 了解完整功能
- 🏗️ 查看 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解架构设计
- 💡 探索 `src/components` 学习组件结构
- 🎨 自定义主题颜色（编辑 `src/index.css`）

## 💻 开发脚本

```bash
# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码检查
npm run lint

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 📦 生产部署

### 构建

```bash
npm run build
```

构建产物在 `dist/` 目录

### 部署到 Vercel

```bash
vercel deploy
```

### 部署到 Netlify

```bash
netlify deploy --prod
```

### 使用 Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🎓 学习资源

- [React 官方文档](https://react.dev/)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [TailwindCSS 文档](https://tailwindcss.com/docs)
- [TanStack Query 指南](https://tanstack.com/query/latest)

## 🆘 获取帮助

- 提交 Issue 反馈问题
- 查看现有文档
- 联系开发团队

---

**祝您使用愉快！** 🎉
