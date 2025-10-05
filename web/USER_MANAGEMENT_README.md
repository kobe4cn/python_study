# 用户权限管理系统 - 使用指南

## 📋 概述

本系统为RAG文档处理系统添加了完整的用户权限管理功能，包括用户认证、角色管理和细粒度权限控制。

## 🎯 功能特性

### 1. 用户认证
- ✅ 用户登录/登出
- ✅ 会话管理
- ✅ Token认证
- ✅ 记住我功能

### 2. 角色系统
- **管理员 (admin)**: 所有权限，可管理用户和系统设置
- **编辑者 (editor)**: 可管理文档和集合，执行搜索
- **查看者 (viewer)**: 只能查看文档和执行搜索

### 3. 权限管理
- ✅ 9种细粒度权限
- ✅ 基于角色的预设权限
- ✅ 自定义权限配置
- ✅ 权限守卫组件
- ✅ 路由级权限保护

### 4. 用户管理
- ✅ 用户列表（表格/网格视图）
- ✅ 创建/编辑/删除用户
- ✅ 用户搜索和筛选
- ✅ 批量操作
- ✅ 用户详情页
- ✅ 激活/禁用用户

### 5. 个人资料
- ✅ 查看和编辑个人信息
- ✅ 修改密码
- ✅ 查看自己的权限

## 📁 文件结构

```
web/
├── src/
│   ├── types/index.ts                          # 类型定义（已更新）
│   ├── services/api.ts                         # API服务（已更新）
│   ├── store/
│   │   └── auth.ts                             # 认证状态管理 ✨新增
│   ├── hooks/
│   │   ├── useAuth.ts                          # 认证Hook ✨新增
│   │   ├── usePermissions.ts                   # 权限Hook ✨新增
│   │   └── useUsers.ts                         # 用户管理Hook ✨新增
│   ├── components/
│   │   ├── auth/
│   │   │   ├── PermissionGuard.tsx             # 权限守卫组件 ✨新增
│   │   │   └── ProtectedRoute.tsx              # 保护路由组件 ✨新增
│   │   └── users/
│   │       ├── UserAvatar.tsx                  # 用户头像 ✨新增
│   │       ├── RoleSelector.tsx                # 角色选择器 ✨新增
│   │       ├── PermissionEditor.tsx            # 权限编辑器 ✨新增
│   │       ├── UserForm.tsx                    # 用户表单 ✨新增
│   │       ├── UserCard.tsx                    # 用户卡片 ✨新增
│   │       └── UserList.tsx                    # 用户列表 ✨新增
│   ├── pages/
│   │   ├── Login.tsx                           # 登录页面 ✨新增
│   │   ├── Users.tsx                           # 用户管理页 ✨新增
│   │   ├── UserDetail.tsx                      # 用户详情页 ✨新增
│   │   └── Profile.tsx                         # 个人资料页 ✨新增
│   └── App.tsx                                 # 路由配置（已更新）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/kevin/dev/ai/homework/web
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

### 3. 访问系统

打开浏览器访问：`http://localhost:5173`

### 4. 测试账号

系统提供了三个演示账号：

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 所有权限 |
| 编辑者 | editor | editor123 | 文档、集合、搜索 |
| 查看者 | viewer | viewer123 | 查看和搜索 |

## 📖 路由说明

| 路由 | 页面 | 权限要求 | 说明 |
|------|------|----------|------|
| `/login` | 登录页 | 无 | 用户登录 |
| `/` | 仪表板 | 已登录 | 系统首页 |
| `/documents` | 文档管理 | `document:read` | 文档列表 |
| `/search` | 搜索 | `search:execute` | 文档搜索 |
| `/collections` | 集合管理 | `collection:read` | 集合列表 |
| `/users` | 用户管理 | `user:manage` | 用户列表（仅管理员） |
| `/users/:id` | 用户详情 | `user:manage` | 用户详情（仅管理员） |
| `/profile` | 个人资料 | 已登录 | 当前用户资料 |

## 🎨 UI组件使用示例

### 1. 权限守卫组件

```tsx
import { PermissionGuard } from '@/components/auth/PermissionGuard'

// 单个权限
<PermissionGuard permission="document:create">
  <Button>上传文档</Button>
</PermissionGuard>

// 多个权限（任一满足）
<PermissionGuard permissions={["document:update", "document:delete"]}>
  <Button>编辑</Button>
</PermissionGuard>

// 多个权限（全部满足）
<PermissionGuard permissions={["document:update", "user:manage"]} requireAll>
  <Button>高级操作</Button>
</PermissionGuard>
```

### 2. 保护路由

```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

<Route
  path="/users"
  element={
    <ProtectedRoute permission="user:manage">
      <Users />
    </ProtectedRoute>
  }
/>
```

### 3. 权限检查Hook

```tsx
import { usePermissions } from '@/hooks/usePermissions'

function MyComponent() {
  const { hasPermission, hasAnyPermission } = usePermissions()

  if (hasPermission("document:create")) {
    return <UploadButton />
  }

  if (hasAnyPermission(["document:update", "document:delete"])) {
    return <EditButton />
  }

  return null
}
```

## 🔐 权限列表

| 权限代码 | 中文名称 | 说明 |
|----------|----------|------|
| `document:create` | 创建/上传文档 | 可以上传新文档 |
| `document:read` | 查看文档 | 可以查看文档内容 |
| `document:update` | 更新文档 | 可以修改文档元数据 |
| `document:delete` | 删除文档 | 可以删除文档 |
| `collection:create` | 创建集合 | 可以创建新集合 |
| `collection:read` | 查看集合 | 可以查看集合列表 |
| `collection:delete` | 删除集合 | 可以删除集合 |
| `search:execute` | 执行搜索 | 可以搜索文档 |
| `user:manage` | 管理用户 | 可以管理用户和权限（仅管理员） |

## 🎯 核心功能演示

### 1. 登录流程

1. 访问 `/login` 页面
2. 输入用户名和密码
3. 点击登录按钮
4. 系统验证后跳转到首页
5. Token保存在localStorage

### 2. 用户管理流程

1. 以管理员身份登录
2. 访问 `/users` 页面
3. 查看用户列表
4. 点击"新增用户"创建用户
5. 填写表单并选择角色
6. 自定义权限（可选）
7. 保存用户

### 3. 权限配置流程

1. 选择用户角色（admin/editor/viewer）
2. 系统自动设置预设权限
3. 展开"自定义权限配置"
4. 勾选或取消勾选权限
5. 保存配置

### 4. 修改密码流程

1. 访问 `/profile` 页面
2. 切换到"安全设置"标签
3. 输入当前密码
4. 输入新密码（两次）
5. 点击"修改密码"
6. 系统自动退出，需重新登录

## 🔧 技术栈

- **React 18**: UI框架
- **TypeScript**: 类型安全
- **TailwindCSS**: 样式系统
- **React Router v6**: 路由管理
- **React Query**: 数据获取
- **Zustand**: 状态管理
- **React Hook Form**: 表单处理
- **date-fns**: 日期格式化
- **react-hot-toast**: 通知提示
- **Radix UI**: 无障碍组件

## 🎨 设计规范

### 颜色系统

```typescript
// 角色徽章
admin: "bg-red-100 text-red-800 border-red-300"     // 红色
editor: "bg-blue-100 text-blue-800 border-blue-300" // 蓝色
viewer: "bg-gray-100 text-gray-800 border-gray-300" // 灰色

// 状态指示
active: "text-green-600"    // 绿色
inactive: "text-gray-400"   // 灰色
```

### 图标系统

```
🛡️ 管理员
✏️ 编辑者
👁️ 查看者
✅ 激活
❌ 禁用
🔒 权限
📄 文档
📁 集合
🔍 搜索
👥 用户
```

## 📝 开发注意事项

### 1. API端点

确保后端实现以下API端点：

```
POST   /api/v1/auth/login           # 用户登录
POST   /api/v1/auth/logout          # 用户登出
GET    /api/v1/auth/me              # 获取当前用户
POST   /api/v1/auth/change-password # 修改密码

GET    /api/v1/users                # 获取用户列表
POST   /api/v1/users                # 创建用户
GET    /api/v1/users/:id            # 获取用户详情
PATCH  /api/v1/users/:id            # 更新用户
DELETE /api/v1/users/:id            # 删除用户
PATCH  /api/v1/users/:id/active     # 激活/禁用用户
POST   /api/v1/users/:id/reset-password # 重置密码
```

### 2. 环境配置

在 `.env` 文件中配置：

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. 类型安全

所有组件都使用TypeScript类型定义，确保：
- 使用导入的类型而不是any
- 为Props定义接口
- 为API响应定义类型

### 4. 错误处理

- 所有API调用都有错误处理
- 使用toast显示错误消息
- 表单验证提供友好提示

## 🐛 常见问题

### Q1: 登录后跳转到登录页？
**A**: 检查Token是否正确保存在localStorage，确保API响应格式正确。

### Q2: 权限检查不生效？
**A**: 确保用户对象包含正确的permissions数组，检查权限字符串是否匹配。

### Q3: 用户列表加载失败？
**A**: 检查API端点是否正确，确保后端返回正确的分页数据格式。

### Q4: 密码强度指示器不显示？
**A**: 检查是否输入了密码，密码强度计算基于长度和字符类型。

## 📚 下一步开发建议

1. **头像上传**: 实现用户头像上传功能
2. **双因素认证**: 添加2FA安全认证
3. **审计日志**: 记录用户操作日志
4. **角色自定义**: 允许创建自定义角色
5. **权限组**: 实现权限组管理
6. **批量操作**: 完善批量激活/删除功能
7. **导出功能**: 导出用户列表为CSV/Excel
8. **邮件通知**: 新用户创建时发送邮件

## 🤝 贡献指南

如需扩展功能：

1. 在 `types/index.ts` 添加新类型
2. 在 `services/api.ts` 添加API方法
3. 在 `hooks/` 创建自定义Hook
4. 在 `components/` 创建可复用组件
5. 在 `pages/` 创建页面组件
6. 在 `App.tsx` 添加路由

## 📄 许可证

MIT License

---

**生成时间**: 2024-10-04
**版本**: 1.0.0
**作者**: Claude AI
