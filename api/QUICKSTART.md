# 快速开始指南

本指南将帮助您在5分钟内启动并运行文档管理API。

## 前置条件

- Python 3.11+
- Docker & Docker Compose (推荐)
- 阿里云DashScope API密钥

## 🚀 方式一：使用Docker Compose (推荐)

### 1. 配置环境变量

```bash
cd api
cp .env.example .env
```

编辑`.env`文件，设置以下必要变量：

```bash
# 阿里云DashScope API密钥（必须）
DASHSCOPE_API_KEY=your-api-key-here

# JWT密钥（必须，生产环境请使用强随机字符串）
SECRET_KEY=your-secret-key-at-least-32-characters-long

# 可选：设置为true启用调试模式
DEBUG=false
```

### 2. 启动所有服务

```bash
docker-compose up -d
```

这将启动：
- FastAPI应用 (端口8000)
- Qdrant向量数据库 (端口6333)
- Redis缓存 (端口6379)
- Nginx反向代理 (端口80/443)

### 3. 验证服务

```bash
# 检查健康状态
curl http://localhost:8000/health

# 查看API文档
open http://localhost:8000/docs
```

### 4. 获取访问令牌

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

保存返回的`access_token`。

### 5. 测试API

```bash
# 设置令牌
TOKEN="your-access-token-here"

# 上传文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf" \
  -F "collection_name=test_docs"

# 搜索文档
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "你的搜索查询",
    "collection_name": "test_docs",
    "top_k": 5
  }'
```

---

## 🐍 方式二：本地Python环境

### 1. 安装依赖

```bash
cd api

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动Qdrant (使用Docker)

```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，设置DASHSCOPE_API_KEY等
```

### 4. 启动API服务

```bash
# 开发模式（自动重载）
./run.sh dev

# 或者直接使用uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 验证和测试

访问 http://localhost:8000/docs 查看交互式API文档。

---

## 🧪 快速测试

### Python测试脚本

创建`test_api.py`:

```python
import requests

# API基础URL
BASE_URL = "http://localhost:8000"

# 1. 健康检查
health = requests.get(f"{BASE_URL}/health")
print(f"健康状态: {health.json()['status']}")

# 2. 登录获取令牌
login = requests.post(
    f"{BASE_URL}/api/v1/auth/token",
    data={"username": "admin", "password": "admin123"}
)
token = login.json()["access_token"]
print(f"✓ 已获取访问令牌")

# 3. 上传文档
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("test.pdf", "rb")}
data = {"collection_name": "test_docs"}

upload = requests.post(
    f"{BASE_URL}/api/v1/documents/upload",
    headers=headers,
    files=files,
    data=data
)
print(f"✓ 文档上传成功: {upload.json()['total_chunks']} 个块")

# 4. 搜索
search = requests.post(
    f"{BASE_URL}/api/v1/search",
    json={
        "query": "测试查询",
        "collection_name": "test_docs",
        "top_k": 5
    }
)
print(f"✓ 搜索完成: 找到 {search.json()['total']} 个结果")
```

运行：

```bash
python test_api.py
```

---

## 🔧 常见问题

### 1. Qdrant连接失败

**问题**: `无法连接到Qdrant (localhost:6333)`

**解决**:
```bash
# 检查Qdrant是否运行
curl http://localhost:6333/health

# 如果未运行，启动Qdrant
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### 2. DashScope API错误

**问题**: `嵌入模型调用失败`

**解决**:
- 检查`.env`中的`DASHSCOPE_API_KEY`是否正确
- 确认API密钥有效且有足够额度
- 检查网络连接

### 3. 文件上传失败

**问题**: `文件类型不支持`

**解决**:
- 确保文件类型在允许列表中（PDF、TXT、MD、DOCX等）
- 检查文件大小是否超过限制（默认50MB）
- 查看`.env`中的`MAX_UPLOAD_SIZE`和`ALLOWED_FILE_TYPES`

### 4. 速率限制错误

**问题**: `429 Too Many Requests`

**解决**:
- 等待一段时间后重试
- 在`.env`中调整速率限制配置
- 使用批量API减少请求次数

---

## 📊 监控面板

### Prometheus指标

访问 http://localhost:8000/metrics 查看Prometheus格式的指标。

### 日志查看

```bash
# Docker Compose日志
docker-compose logs -f api

# 查看最近100行
docker-compose logs --tail=100 api
```

---

## 🛑 停止服务

### Docker Compose

```bash
# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除所有数据（包括卷）
docker-compose down -v
```

### 本地运行

按`Ctrl+C`停止Uvicorn服务器。

---

## 📚 下一步

- 阅读 [API_EXAMPLES.md](./API_EXAMPLES.md) 了解更多API用法
- 查看 [README.md](./README.md) 了解完整功能
- 参考 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解系统架构

---

## 🆘 获取帮助

- 查看API文档: http://localhost:8000/docs
- 检查健康状态: http://localhost:8000/health
- 查看日志排查问题

**祝您使用愉快！** 🎉
