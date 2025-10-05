# 文档管理API - 生产级FastAPI后端

基于FastAPI构建的高性能、可扩展的文档管理系统，支持文档上传、语义搜索、向量存储等功能。

## ✨ 核心特性

### 🚀 高性能

- **异步架构**: 基于asyncio的全异步处理
- **连接池**: 高效的数据库和HTTP连接管理
- **响应缓存**: Redis缓存支持，显著提升响应速度
- **批量处理**: 智能批量文档处理和搜索
- **Gzip压缩**: 自动响应压缩

### 🔒 安全性

- **JWT认证**: 基于JSON Web Token的身份验证
- **API密钥**: 支持API密钥认证（服务间调用）
- **速率限制**: 防止API滥用和DDoS攻击
- **HTTPS支持**: TLS 1.2+加密传输
- **安全头**: 完整的HTTP安全头配置
- **输入验证**: Pydantic V2数据验证
- **路径遍历防护**: 文件上传安全检查

### 📊 可观测性

- **结构化日志**: JSON格式日志，便于分析
- **OpenTelemetry**: 分布式追踪支持
- **Prometheus指标**: 完整的性能指标导出
- **健康检查**: 完善的健康和就绪检查端点
- **请求追踪**: 每个请求的唯一ID追踪

### 🎯 功能完整

- **文档上传**: 支持PDF、TXT、MD、DOCX等多种格式
- **URL加载**: 从网页URL直接加载内容
- **语义搜索**: 基于向量的智能语义搜索
- **批量操作**: 批量文档处理和搜索
- **集合管理**: 灵活的向量存储集合管理
- **元数据过滤**: 基于元数据的精确过滤

## 📋 技术栈

- **Web框架**: FastAPI 0.109+
- **ASGI服务器**: Uvicorn
- **数据验证**: Pydantic V2
- **向量数据库**: Qdrant
- **嵌入模型**: DashScope (阿里云)
- **缓存**: Redis
- **认证**: python-jose, passlib
- **速率限制**: slowapi
- **日志**: structlog, loguru
- **监控**: Prometheus, OpenTelemetry

## 🚀 快速开始

### 1. 环境要求

- Python 3.11+
- Docker & Docker Compose (可选)
- Qdrant 向量数据库
- Redis (可选，用于缓存)

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
cd api
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑.env文件，至少配置以下必要项：
# - DASHSCOPE_API_KEY: 阿里云DashScope API密钥
# - SECRET_KEY: JWT密钥（32位以上随机字符串）
# - QDRANT_HOST: Qdrant服务地址
```

### 4. 启动服务

#### 方式一：直接运行

```bash
# 开发模式
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 方式二：使用Docker Compose

```bash
cd api
docker-compose up -d
```

### 5. 访问API

- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health
- **Prometheus指标**: http://localhost:8000/metrics

## 📖 API端点

### 认证

- `POST /api/v1/auth/token` - 获取访问令牌
- `POST /api/v1/auth/refresh` - 刷新令牌

### 文档管理

- `POST /api/v1/documents/upload` - 上传文件
- `POST /api/v1/documents/from-url` - 从URL加载
- `DELETE /api/v1/documents/{collection_name}` - 删除文档

### 搜索

- `POST /api/v1/search` - 语义搜索
- `POST /api/v1/search/batch` - 批量搜索

### 集合管理

- `GET /api/v1/collections` - 列出所有集合
- `GET /api/v1/collections/{name}/info` - 获取集合信息
- `DELETE /api/v1/collections/{name}` - 删除集合

### 健康检查

- `GET /health` - 健康检查
- `GET /ready` - 就绪检查
- `GET /ping` - Ping

详细使用示例请参考 [API_EXAMPLES.md](./API_EXAMPLES.md)

## 🏗️ 项目结构

```
api/
├── __init__.py
├── main.py                 # FastAPI应用入口
├── config.py              # 配置管理
├── dependencies.py        # 依赖注入
├── middleware/           # 中间件
│   ├── __init__.py
│   ├── auth.py          # 认证中间件
│   ├── rate_limit.py    # 速率限制
│   ├── logging.py       # 日志中间件
│   └── security.py      # 安全中间件
├── routers/             # 路由
│   ├── __init__.py
│   ├── auth.py         # 认证路由
│   ├── documents.py    # 文档路由
│   ├── search.py       # 搜索路由
│   ├── collections.py  # 集合路由
│   └── health.py       # 健康检查
├── models/             # 数据模型
│   ├── __init__.py
│   ├── requests.py     # 请求模型
│   └── responses.py    # 响应模型
├── services/           # 业务逻辑
│   ├── __init__.py
│   ├── document_service.py
│   └── search_service.py
├── security/           # 安全模块
│   ├── __init__.py
│   ├── jwt.py         # JWT处理
│   ├── auth.py        # 认证依赖
│   └── tls.py         # TLS配置
├── requirements.txt    # Python依赖
├── Dockerfile         # Docker镜像
├── docker-compose.yml # Docker Compose配置
├── .env.example       # 环境变量示例
├── README.md          # 本文档
└── API_EXAMPLES.md    # API使用示例
```

## 🔧 配置说明

### 核心配置

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| DEBUG | 调试模式 | false |
| ENVIRONMENT | 运行环境 | production |
| HOST | 服务器地址 | 0.0.0.0 |
| PORT | 服务器端口 | 8000 |
| WORKERS | 工作进程数 | 4 |

### 安全配置

| 配置项 | 说明 | 必填 |
|-------|------|------|
| SECRET_KEY | JWT密钥 | 是 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 访问令牌过期时间 | 否 |
| API_KEYS | API密钥列表 | 否 |
| USE_HTTPS | 启用HTTPS | 否 |

### Qdrant配置

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| QDRANT_HOST | Qdrant主机 | localhost |
| QDRANT_PORT | Qdrant端口 | 6333 |
| QDRANT_COLLECTION | 默认集合 | documents |

### 嵌入模型配置

| 配置项 | 说明 | 必填 |
|-------|------|------|
| DASHSCOPE_API_KEY | DashScope API密钥 | 是 |
| EMBEDDING_MODEL | 嵌入模型名称 | 否 |

完整配置说明请参考 `.env.example`

## 🐳 Docker部署

### 1. 构建镜像

```bash
docker build -t document-api:latest -f api/Dockerfile .
```

### 2. 运行容器

```bash
docker run -d \
  --name document-api \
  -p 8000:8000 \
  -e DASHSCOPE_API_KEY=your-api-key \
  -e QDRANT_HOST=qdrant \
  -v ./uploads:/app/uploads \
  document-api:latest
```

### 3. 使用Docker Compose

```bash
cd api
docker-compose up -d
```

查看日志：

```bash
docker-compose logs -f api
```

停止服务：

```bash
docker-compose down
```

## 🔍 监控和日志

### Prometheus指标

访问 `http://localhost:8000/metrics` 查看指标：

- HTTP请求计数
- 请求延迟分布
- 活跃连接数
- 自定义业务指标

### 日志

日志输出位置：

- 标准输出（stdout）
- 文件日志（可配置）

日志格式：

- JSON格式（生产环境）
- 文本格式（开发环境）

### OpenTelemetry追踪

启用OpenTelemetry后，可将追踪数据导出到Jaeger、Zipkin等后端。

## 🧪 测试

```bash
# 运行测试
pytest api/tests/

# 测试覆盖率
pytest --cov=api api/tests/

# 生成HTML覆盖率报告
pytest --cov=api --cov-report=html api/tests/
```

## 📝 最佳实践

### 1. 生产环境配置

- 使用强随机SECRET_KEY
- 启用HTTPS
- 配置合理的速率限制
- 启用Redis缓存
- 配置日志文件
- 使用多个Worker进程

### 2. 性能优化

- 启用响应缓存
- 使用批量API
- 合理设置chunk_size
- 配置连接池
- 监控并调优top_k参数

### 3. 安全建议

- 定期更新依赖
- 使用强密码策略
- 限制上传文件大小
- 配置CORS白名单
- 启用安全响应头
- 定期审计日志

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题，请提交Issue或联系维护者。

---

**版本**: 1.0.0
**最后更新**: 2025-10-04
