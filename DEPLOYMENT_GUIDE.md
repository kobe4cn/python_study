# RAG问答系统 - 完整部署和使用指南

## 📋 目录

1. [系统概览](#系统概览)
2. [技术栈](#技术栈)
3. [前置要求](#前置要求)
4. [数据库配置](#数据库配置)
   - [PostgreSQL配置](#postgresql配置)
   - [Redis配置](#redis配置)
   - [Qdrant配置](#qdrant配置)
5. [后端部署](#后端部署)
6. [前端部署](#前端部署)
7. [TLS/HTTPS配置](#tlshttps配置)
8. [Docker部署](#docker部署)
9. [API使用示例](#api使用示例)
10. [前端UI使用](#前端ui使用)
11. [故障排除](#故障排除)

---

## 系统概览

本系统是一个完整的RAG（检索增强生成）问答系统，包含：

- **后端API**: FastAPI + TLS/HTTPS
- **RAG工作流**: LangGraph + Qdrant向量数据库
- **前端UI**: React + TypeScript + Tailwind CSS
- **认证安全**: JWT + API Key + 速率限制
- **数据存储**: PostgreSQL (用户/会话) + Qdrant (向量) + Redis (缓存)

### 系统架构

```
┌─────────────┐      HTTPS/WSS      ┌──────────────┐      ┌──────────────┐
│  React UI   │◄────────────────────►│  FastAPI     │◄────►│  LangGraph   │
│  (Frontend) │                      │  (Backend)   │      │  (RAG Engine)│
└─────────────┘                      └──────────────┘      └──────────────┘
                                            │                      │
                    ┌───────────────────────┼──────────────────────┘
                    │                       │
                    ▼                       ▼                      ▼
             ┌──────────────┐       ┌──────────────┐      ┌──────────────┐
             │  PostgreSQL  │       │    Redis     │      │   Qdrant     │
             │  (用户/会话) │       │    (缓存)    │      │  (向量存储)  │
             └──────────────┘       └──────────────┘      └──────────────┘
```

---

## 技术栈

### 后端
- **框架**: FastAPI 0.109+
- **服务器**: Uvicorn with TLS support
- **安全**: JWT, python-jose, passlib
- **限流**: slowapi
- **流式**: SSE (Server-Sent Events) via sse-starlette
- **RAG**: LangGraph + LangChain + Qdrant
- **数据库**: PostgreSQL (SQLAlchemy ORM)
- **缓存**: Redis
- **向量**: Qdrant

### 前端
- **框架**: React 18 + TypeScript
- **状态**: Zustand + React Query
- **UI**: Tailwind CSS + Radix UI
- **HTTP**: Fetch API with EventSource for SSE
- **Markdown**: react-markdown

---

## 前置要求

### 软件版本要求

```bash
# Python 3.10+
python --version

# Node.js 18+
node --version

# Docker & Docker Compose
docker --version
docker-compose --version

# PostgreSQL 14+ (可选，推荐用Docker)
psql --version

# Redis 7+ (可选，推荐用Docker)
redis-cli --version
```

### 硬件要求

**最低配置（开发环境）：**
- CPU: 2核
- 内存: 4GB
- 磁盘: 10GB

**推荐配置（生产环境）：**
- CPU: 4核+
- 内存: 8GB+
- 磁盘: 50GB+ (SSD)

---

## 数据库配置

### PostgreSQL配置

#### 方式1: Docker安装（推荐）

```bash
# 1. 创建数据目录
mkdir -p ~/data/postgres

# 2. 启动PostgreSQL容器
docker run -d \
  --name homework-postgres \
  -e POSTGRES_USER=homework \
  -e POSTGRES_PASSWORD=your-secure-password \
  -e POSTGRES_DB=homework_db \
  -p 5432:5432 \
  -v ~/data/postgres:/var/lib/postgresql/data \
  postgres:14-alpine

# 3. 验证连接
docker exec -it homework-postgres psql -U homework -d homework_db

# 4. 查看数据库列表
\l

# 5. 退出
\q
```

#### 方式2: 本地安装

**Ubuntu/Debian:**
```bash
# 安装PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 切换到postgres用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE homework_db;
CREATE USER homework WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE homework_db TO homework;

# 退出
\q
```

**macOS:**
```bash
# 使用Homebrew安装
brew install postgresql@14

# 启动服务
brew services start postgresql@14

# 创建数据库
createdb homework_db

# 连接数据库
psql homework_db
```

**Windows:**
```powershell
# 下载并安装: https://www.postgresql.org/download/windows/

# 使用pgAdmin或命令行创建数据库
psql -U postgres
CREATE DATABASE homework_db;
```

#### 初始化数据库表

```bash
# 方式1: 使用Alembic迁移（推荐）
cd api
source venv/bin/activate

# 初始化Alembic
alembic init alembic

# 编辑alembic.ini中的数据库URL
# sqlalchemy.url = postgresql://homework:password@localhost/homework_db

# 生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head

# 方式2: 使用SQL脚本直接初始化
psql -U homework -d homework_db -f api/scripts/init_db.sql
```

#### 创建初始化SQL脚本

创建 `api/scripts/init_db.sql`:

```sql
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT
);

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- 会话表（用于聊天历史）
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

-- 插入默认角色
INSERT INTO roles (name, description) VALUES
    ('admin', '系统管理员'),
    ('user', '普通用户')
ON CONFLICT (name) DO NOTHING;

-- 插入默认权限
INSERT INTO permissions (name, resource, action, description) VALUES
    ('chat:read', 'chat', 'read', '查看聊天记录'),
    ('chat:write', 'chat', 'write', '发送聊天消息'),
    ('documents:read', 'documents', 'read', '查看文档'),
    ('documents:write', 'documents', 'write', '上传文档'),
    ('documents:delete', 'documents', 'delete', '删除文档'),
    ('users:read', 'users', 'read', '查看用户'),
    ('users:write', 'users', 'write', '管理用户')
ON CONFLICT (name) DO NOTHING;

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### 创建初始管理员用户

创建 `api/scripts/create_admin.py`:

```python
"""
创建初始管理员用户脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.database.session import SessionLocal
from api.models.users import User, Role
from api.security.auth import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user():
    """创建管理员用户"""
    db = SessionLocal()

    try:
        # 检查是否已存在admin用户
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            logger.warning("管理员用户已存在")
            return

        # 获取admin角色
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            logger.error("admin角色不存在，请先运行数据库初始化")
            return

        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="系统管理员",
            hashed_password=get_password_hash("admin123"),  # 请在生产环境修改密码
            is_active=True,
            is_superuser=True
        )

        admin_user.roles.append(admin_role)

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info(f"✅ 管理员用户创建成功: {admin_user.username}")
        logger.info("⚠️  默认密码: admin123 (请立即修改)")

    except Exception as e:
        logger.error(f"创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
```

运行创建管理员用户：
```bash
cd api
python scripts/create_admin.py
```

### Redis配置

#### 方式1: Docker安装（推荐）

```bash
# 1. 创建数据目录
mkdir -p ~/data/redis

# 2. 启动Redis容器
docker run -d \
  --name homework-redis \
  -p 6379:6379 \
  -v ~/data/redis:/data \
  redis:7-alpine \
  redis-server --appendonly yes --requirepass your-redis-password

# 3. 验证连接
docker exec -it homework-redis redis-cli

# 4. 认证
AUTH your-redis-password

# 5. 测试
PING
# 应返回: PONG

# 6. 查看信息
INFO server

# 7. 退出
EXIT
```

#### 方式2: 本地安装

**Ubuntu/Debian:**
```bash
# 安装Redis
sudo apt update
sudo apt install redis-server

# 配置密码
sudo nano /etc/redis/redis.conf
# 找到 # requirepass foobared
# 修改为: requirepass your-redis-password

# 重启服务
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# 测试连接
redis-cli
AUTH your-redis-password
PING
```

**macOS:**
```bash
# 使用Homebrew安装
brew install redis

# 启动服务
brew services start redis

# 测试连接
redis-cli ping
```

**Windows:**
```powershell
# 下载并安装: https://github.com/microsoftarchive/redis/releases
# 或使用WSL2安装Linux版本

# 启动服务
redis-server

# 测试连接
redis-cli ping
```

#### Redis配置文件示例

创建 `api/config/redis.conf`:

```conf
# Redis配置文件

# 网络
bind 127.0.0.1
port 6379
timeout 0
tcp-keepalive 300

# 安全
requirepass your-redis-password
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# 持久化
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfilename "appendonly.aof"

# 内存管理
maxmemory 256mb
maxmemory-policy allkeys-lru

# 日志
loglevel notice
logfile "/var/log/redis/redis.log"

# 性能
databases 16
```

使用自定义配置启动Redis:
```bash
redis-server /path/to/redis.conf
```

### Qdrant配置

#### Docker安装（推荐）

```bash
# 1. 创建数据目录
mkdir -p ~/data/qdrant

# 2. 启动Qdrant容器
docker run -d \
  --name homework-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v ~/data/qdrant:/qdrant/storage \
  qdrant/qdrant

# 3. 验证连接
curl http://localhost:6333

# 4. 查看集合列表
curl http://localhost:6333/collections

# 5. Web UI访问
# 访问: http://localhost:6333/dashboard
```

#### Qdrant集合初始化

创建 `api/scripts/init_qdrant.py`:

```python
"""
初始化Qdrant向量数据库集合
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_qdrant_collection():
    """初始化Qdrant集合"""
    # 连接Qdrant
    client = QdrantClient(host="localhost", port=6333)

    collection_name = "documents"
    vector_size = 1536  # text-embedding-ada-002的维度

    try:
        # 检查集合是否存在
        collections = client.get_collections().collections
        exists = any(col.name == collection_name for col in collections)

        if exists:
            logger.info(f"集合 '{collection_name}' 已存在")
            return

        # 创建集合
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        logger.info(f"✅ 集合 '{collection_name}' 创建成功")
        logger.info(f"   - 向量维度: {vector_size}")
        logger.info(f"   - 距离度量: COSINE")

    except Exception as e:
        logger.error(f"初始化Qdrant集合失败: {e}")
        raise


if __name__ == "__main__":
    init_qdrant_collection()
```

运行初始化：
```bash
cd api
python scripts/init_qdrant.py
```

---

## 后端部署

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd homework
```

### 2. 创建Python虚拟环境

```bash
cd api
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt

# 如果使用PostgreSQL，还需要安装
pip install psycopg2-binary alembic

# 如果使用Redis
pip install redis
```

### 4. 环境变量配置

创建 `api/.env` 文件：

```bash
# === 应用配置 ===
APP_NAME=RAG问答系统
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False

# === 服务器配置 ===
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=False

# === TLS/HTTPS配置 ===
USE_HTTPS=True
SSL_CERTFILE=./certs/cert.pem
SSL_KEYFILE=./certs/key.pem
# SSL_CA_CERTS=./certs/ca-cert.pem  # 可选

# === CORS配置 ===
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com", "http://localhost:5173"]
CORS_ALLOW_CREDENTIALS=True

# === JWT密钥 ===
SECRET_KEY=your-secret-key-change-this-to-random-64-chars-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# === LLM配置 ===
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# === PostgreSQL配置 ===
DATABASE_URL=postgresql://homework:your-secure-password@localhost:5432/homework_db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_ECHO=False

# === Redis配置 ===
REDIS_ENABLED=True
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-redis-password
CACHE_TTL=300

# === Qdrant配置 ===
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents
QDRANT_USER=
QDRANT_PASSWORD=

# === 嵌入模型配置 ===
EMBEDDING_MODEL=text-embedding-v4
EMBEDDING_BATCH_SIZE=100

# === 文档处理配置 ===
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5

# === 速率限制 ===
RATE_LIMIT_ENABLED=True
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_UPLOAD=10/minute
RATE_LIMIT_SEARCH=50/minute

# === 文件上传配置 ===
MAX_UPLOAD_SIZE=52428800  # 50MB
UPLOAD_DIR=./uploads

# === 日志配置 ===
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=./logs/app.log

# === 监控配置 ===
PROMETHEUS_ENABLED=True
PROMETHEUS_PATH=/metrics
OTEL_ENABLED=False
OTEL_EXPORTER_ENDPOINT=
```

### 5. 初始化数据库

```bash
# 初始化PostgreSQL
psql -U homework -d homework_db -f scripts/init_db.sql

# 或使用Alembic
alembic upgrade head

# 创建管理员用户
python scripts/create_admin.py

# 初始化Qdrant集合
python scripts/init_qdrant.py
```

### 6. 生成TLS证书

#### 开发环境（自签名证书）

```bash
# 创建证书目录
mkdir -p certs

# 生成自签名证书
python -c "from api.security.tls import generate_self_signed_cert; generate_self_signed_cert('./certs/cert.pem', './certs/key.pem', days_valid=365)"
```

#### 生产环境（Let's Encrypt）

```bash
# 安装certbot
sudo apt install certbot  # Ubuntu/Debian
# brew install certbot  # macOS

# 生成证书（需要域名）
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 证书位置（更新.env）
# SSL_CERTFILE=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
# SSL_KEYFILE=/etc/letsencrypt/live/yourdomain.com/privkey.pem

# 设置自动续期
sudo crontab -e
# 添加: 0 0 1 * * certbot renew --quiet
```

### 7. 启动服务

#### 开发模式

```bash
python main.py
```

#### 生产模式

```bash
# 方式1: 直接使用uvicorn
uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --ssl-certfile ./certs/cert.pem \
  --ssl-keyfile ./certs/key.pem \
  --log-level info

# 方式2: 使用systemd服务
sudo cp api/scripts/homework-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable homework-api
sudo systemctl start homework-api
sudo systemctl status homework-api
```

创建 `api/scripts/homework-api.service`:

```ini
[Unit]
Description=RAG问答系统 FastAPI服务
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/homework/api
Environment="PATH=/var/www/homework/api/venv/bin"
ExecStart=/var/www/homework/api/venv/bin/uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --ssl-certfile /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
    --ssl-keyfile /etc/letsencrypt/live/yourdomain.com/privkey.pem

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8. 验证部署

```bash
# 健康检查
curl -k https://localhost:8000/health

# 数据库连接检查
curl -k https://localhost:8000/health | jq '.database'

# Redis连接检查
curl -k https://localhost:8000/health | jq '.redis'

# Qdrant连接检查
curl -k https://localhost:8000/health | jq '.qdrant'

# API文档（仅开发模式）
# 访问: https://localhost:8000/docs
```

---

## 前端部署

### 1. 安装依赖

```bash
cd web
npm install
```

### 2. 环境变量配置

创建 `web/.env`:

```bash
# API地址
VITE_API_URL=https://api.yourdomain.com

# 或开发环境
# VITE_API_URL=https://localhost:8000
```

### 3. 构建生产版本

```bash
# 构建
npm run build

# 预览
npm run preview
```

### 4. 部署到服务器

#### 方式1: Nginx

安装Nginx:
```bash
sudo apt install nginx  # Ubuntu/Debian
# brew install nginx  # macOS
```

创建 `/etc/nginx/sites-available/homework`:

```nginx
# HTTP重定向到HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    return 301 https://$server_name$request_uri;
}

# HTTPS服务器
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL证书
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 前端静态文件
    location / {
        root /var/www/homework/web/dist;
        try_files $uri $uri/ /index.html;

        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API代理
    location /api/ {
        proxy_pass https://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE支持
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;

        # 超时设置
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
}
```

启用站点:
```bash
sudo ln -s /etc/nginx/sites-available/homework /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 方式2: Vercel/Netlify

```bash
# 构建
npm run build

# 上传 dist/ 目录到Vercel或Netlify
```

---

## Docker部署

### Docker Compose完整配置

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:14-alpine
    container_name: homework-postgres
    environment:
      POSTGRES_USER: homework
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secure-password}
      POSTGRES_DB: homework_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./api/scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U homework"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - homework-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: homework-redis
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis-password} --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - homework-network

  # Qdrant向量数据库
  qdrant:
    image: qdrant/qdrant:latest
    container_name: homework-qdrant
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
      - "6334:6334"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - homework-network

  # FastAPI后端
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: homework-api
    env_file:
      - ./api/.env
    environment:
      DATABASE_URL: postgresql://homework:${POSTGRES_PASSWORD:-secure-password}@postgres:5432/homework_db
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD:-redis-password}
      QDRANT_HOST: qdrant
    volumes:
      - ./api:/app
      - api_uploads:/app/uploads
      - api_logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - homework-network

  # React前端
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    container_name: homework-web
    environment:
      VITE_API_URL: https://api.yourdomain.com
    ports:
      - "5173:80"
    depends_on:
      - api
    networks:
      - homework-network

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  api_uploads:
  api_logs:

networks:
  homework-network:
    driver: bridge
```

### 启动所有服务

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api

# 停止所有服务
docker-compose down

# 停止并删除所有数据
docker-compose down -v
```

### 初始化数据

```bash
# 等待所有服务启动
sleep 30

# 初始化数据库
docker-compose exec api python scripts/create_admin.py
docker-compose exec api python scripts/init_qdrant.py
```

---

## API使用示例

### 1. 认证

```bash
# 登录获取token
curl -X POST https://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# 响应
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. 流式问答（SSE）

```bash
# 使用curl测试SSE
curl -X POST https://localhost:8000/api/v1/chat/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是RAG?",
    "max_retries": 3,
    "include_sources": true,
    "include_workflow": true
  }' \
  --no-buffer

# 响应（SSE流）
event: start
data: {"query": "什么是RAG?", "timestamp": "2025-10-05T10:00:00"}

event: workflow_step
data: {"loop_step": 1, "answers": 0, "max_retries": 3}

event: documents
data: {"count": 3, "documents": [...]}

event: chunk
data: {"content": "RAG是检索增强生成..."}

event: done
data: {"status": "completed", "final_answer": "..."}
```

### 3. 非流式问答

```bash
curl -X POST https://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是向量数据库?",
    "stream": false
  }'
```

---

## 前端UI使用

### 1. 登录

访问 `https://yourdomain.com/login`

### 2. 聊天界面

访问 `https://yourdomain.com/chat`

---

## 故障排除

### 数据库相关

#### PostgreSQL连接失败

```bash
# 检查服务状态
sudo systemctl status postgresql
docker ps | grep postgres

# 检查端口
netstat -an | grep 5432

# 测试连接
psql -U homework -h localhost -d homework_db

# 查看日志
docker logs homework-postgres
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### Redis连接失败

```bash
# 检查服务状态
sudo systemctl status redis
docker ps | grep redis

# 测试连接
redis-cli -h localhost -p 6379 -a your-password ping

# 查看日志
docker logs homework-redis
```

#### Qdrant连接失败

```bash
# 检查服务
docker ps | grep qdrant

# 测试连接
curl http://localhost:6333/health

# 查看日志
docker logs homework-qdrant
```

### 其他常见问题

参考原文档的故障排除部分...

---

## 监控和维护

### 数据库备份

```bash
# PostgreSQL备份
docker exec homework-postgres pg_dump -U homework homework_db > backup_$(date +%Y%m%d).sql

# 恢复
docker exec -i homework-postgres psql -U homework homework_db < backup.sql

# Redis备份
docker exec homework-redis redis-cli SAVE

# Qdrant备份
cp -r ~/data/qdrant ~/backups/qdrant_$(date +%Y%m%d)
```

### 监控指标

访问:
- Prometheus指标: `https://localhost:8000/metrics`
- Qdrant Dashboard: `http://localhost:6333/dashboard`

---

**版本**: 1.0.1
**最后更新**: 2025-10-05
**维护者**: AI Assistant Team
