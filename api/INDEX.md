# 文档管理API - 文件索引

本文档提供所有项目文件的快速导航。

## 📁 目录结构

```
api/
├── README.md                      # 项目主文档
├── PROJECT_SUMMARY.md             # 项目交付总结
├── QUICKSTART.md                  # 快速开始指南
├── API_EXAMPLES.md                # API使用示例
├── ARCHITECTURE.md                # 系统架构文档
├── INDEX.md                       # 本文件
│
├── main.py                        # FastAPI应用入口
├── config.py                      # 配置管理
├── dependencies.py                # 依赖注入
│
├── routers/                       # 路由层
│   ├── __init__.py
│   ├── auth.py                   # 认证路由
│   ├── documents.py              # 文档管理路由
│   ├── search.py                 # 搜索路由
│   ├── collections.py            # 集合管理路由
│   └── health.py                 # 健康检查路由
│
├── models/                        # 数据模型
│   ├── __init__.py
│   ├── requests.py               # 请求模型
│   └── responses.py              # 响应模型
│
├── services/                      # 业务逻辑
│   ├── __init__.py
│   ├── document_service.py       # 文档处理服务
│   └── search_service.py         # 搜索服务
│
├── security/                      # 安全模块
│   ├── __init__.py
│   ├── jwt.py                    # JWT令牌管理
│   ├── auth.py                   # 认证依赖
│   └── tls.py                    # TLS/SSL配置
│
├── middleware/                    # 中间件
│   ├── __init__.py
│   ├── logging.py                # 日志中间件
│   ├── rate_limit.py             # 速率限制
│   └── security.py               # 安全中间件
│
├── tests/                         # 测试
│   ├── __init__.py
│   └── test_api.py               # API测试
│
├── requirements.txt               # Python依赖
├── Dockerfile                     # Docker镜像
├── docker-compose.yml             # 容器编排
├── .env.example                   # 环境变量模板
└── run.sh                         # 启动脚本
```

## 📖 文档导航

### 入门指南
1. **[QUICKSTART.md](./QUICKSTART.md)** - 5分钟快速开始
   - Docker Compose部署
   - 本地Python环境
   - 快速测试

2. **[README.md](./README.md)** - 完整项目文档
   - 功能特性
   - 技术栈
   - 配置说明
   - 部署指南

### 使用指南
3. **[API_EXAMPLES.md](./API_EXAMPLES.md)** - API使用示例
   - 认证示例
   - 文档上传
   - 搜索查询
   - Python客户端

### 架构文档
4. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 系统架构
   - 架构图
   - 组件说明
   - 数据流
   - 部署架构

### 总结报告
5. **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - 项目交付总结
   - 交付清单
   - 功能清单
   - 技术栈
   - 亮点特性

## 🔍 按功能查找文件

### 认证和安全
- `security/jwt.py` - JWT令牌创建和验证
- `security/auth.py` - 用户认证和授权
- `security/tls.py` - HTTPS配置
- `routers/auth.py` - 认证API端点
- `middleware/security.py` - 安全中间件

### 文档处理
- `services/document_service.py` - 文档处理业务逻辑
- `routers/documents.py` - 文档管理API
- `dependencies.py` - 文档加载器和分割器

### 搜索功能
- `services/search_service.py` - 搜索业务逻辑
- `routers/search.py` - 搜索API端点
- `dependencies.py` - 向量存储客户端

### 配置和部署
- `config.py` - 完整配置系统
- `.env.example` - 环境变量模板
- `Dockerfile` - Docker镜像构建
- `docker-compose.yml` - 容器编排
- `run.sh` - 启动脚本

### 监控和日志
- `middleware/logging.py` - 日志中间件
- `routers/health.py` - 健康检查
- `main.py` - Prometheus指标配置

## 🚀 快速链接

### 开始使用
```bash
# 1. 配置环境
cp .env.example .env
# 编辑.env文件

# 2. 启动服务
docker-compose up -d

# 3. 访问文档
open http://localhost:8000/docs
```

### 核心API端点
- 认证: `POST /api/v1/auth/token`
- 上传: `POST /api/v1/documents/upload`
- 搜索: `POST /api/v1/search`
- 健康: `GET /health`

### 关键配置
- `DASHSCOPE_API_KEY` - 嵌入模型API密钥
- `SECRET_KEY` - JWT密钥
- `QDRANT_HOST` - Qdrant地址
- `REDIS_ENABLED` - 启用缓存

## 📊 文件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Python文件 | 27 | 应用代码 |
| 文档文件 | 6 | Markdown文档 |
| 配置文件 | 4 | 环境和部署配置 |
| 总计 | 37+ | 完整项目文件 |

## 🎯 推荐阅读顺序

### 新用户
1. README.md - 了解项目
2. QUICKSTART.md - 快速上手
3. API_EXAMPLES.md - 学习API使用

### 开发者
1. ARCHITECTURE.md - 理解架构
2. main.py - 查看应用入口
3. services/ - 了解业务逻辑

### 运维人员
1. docker-compose.yml - 部署配置
2. .env.example - 环境变量
3. run.sh - 启动脚本

---

**最后更新**: 2025-10-04
**版本**: 1.0.0
