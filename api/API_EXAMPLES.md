# API使用示例

本文档提供了文档管理API的详细使用示例。

## 目录

1. [认证](#认证)
2. [文档上传](#文档上传)
3. [URL加载](#url加载)
4. [语义搜索](#语义搜索)
5. [集合管理](#集合管理)
6. [健康检查](#健康检查)

---

## 认证

### 1. 获取访问令牌

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**响应示例:**

```json
{
  "success": true,
  "message": "登录成功",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "timestamp": "2025-10-04T12:00:00Z"
}
```

### 2. 使用访问令牌

在后续请求中添加Authorization头：

```bash
curl -X GET "http://localhost:8000/api/v1/collections" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. 刷新令牌

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

## 文档上传

### 1. 上传单个文件

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "collection_name=my_documents" \
  -F "chunk_size=1000" \
  -F "chunk_overlap=200"
```

**响应示例:**

```json
{
  "success": true,
  "message": "文件上传成功",
  "doc_ids": ["doc_001", "doc_002", "doc_003"],
  "total_chunks": 3,
  "collection_name": "my_documents",
  "file_name": "document.pdf",
  "file_size": 1048576,
  "errors": [],
  "timestamp": "2025-10-04T12:00:00Z"
}
```

### 2. Python示例

```python
import requests

url = "http://localhost:8000/api/v1/documents/upload"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}

files = {
    "file": open("document.pdf", "rb")
}

data = {
    "collection_name": "my_documents",
    "chunk_size": 1000,
    "chunk_overlap": 200
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

---

## URL加载

### 1. 从URL加载文档

```bash
curl -X POST "http://localhost:8000/api/v1/documents/from-url" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/article1",
      "https://example.com/article2"
    ],
    "collection_name": "web_articles",
    "metadata": {
      "source_type": "web",
      "category": "技术文章"
    },
    "chunk_size": 1500,
    "chunk_overlap": 300
  }'
```

**响应示例:**

```json
{
  "success": true,
  "message": "成功加载 2 个URL",
  "doc_ids": ["web_001", "web_002", "web_003", "web_004"],
  "total_chunks": 4,
  "collection_name": "web_articles",
  "urls_loaded": 2,
  "urls_failed": 0,
  "errors": [],
  "timestamp": "2025-10-04T12:00:00Z"
}
```

### 2. Python示例

```python
import requests

url = "http://localhost:8000/api/v1/documents/from-url"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Content-Type": "application/json"
}

payload = {
    "urls": [
        "https://example.com/article1",
        "https://example.com/article2"
    ],
    "collection_name": "web_articles",
    "metadata": {
        "source_type": "web"
    }
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

---

## 语义搜索

### 1. 基础搜索

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是机器学习？",
    "collection_name": "my_documents",
    "top_k": 5
  }'
```

**响应示例:**

```json
{
  "success": true,
  "query": "什么是机器学习？",
  "results": [
    {
      "doc_id": "doc_001",
      "content": "机器学习是人工智能的一个分支...",
      "score": 0.95,
      "metadata": {
        "source": "ml_intro.pdf",
        "page": 1
      }
    },
    {
      "doc_id": "doc_002",
      "content": "深度学习是机器学习的子集...",
      "score": 0.89,
      "metadata": {
        "source": "dl_basics.pdf",
        "page": 3
      }
    }
  ],
  "total": 2,
  "took_ms": 45.23,
  "collection_name": "my_documents",
  "timestamp": "2025-10-04T12:00:00Z"
}
```

### 2. 带元数据过滤的搜索

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "深度学习算法",
    "collection_name": "my_documents",
    "top_k": 3,
    "filter_metadata": {
      "source_type": "paper",
      "year": 2024
    }
  }'
```

### 3. 批量搜索

```bash
curl -X POST "http://localhost:8000/api/v1/search/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "什么是神经网络？",
      "卷积神经网络的应用",
      "自然语言处理技术"
    ],
    "collection_name": "my_documents",
    "top_k": 3
  }'
```

### 4. Python示例

```python
import requests

# 基础搜索
def search_documents(query, collection="my_documents", top_k=5):
    url = "http://localhost:8000/api/v1/search"
    headers = {"Content-Type": "application/json"}

    payload = {
        "query": query,
        "collection_name": collection,
        "top_k": top_k
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 使用
results = search_documents("机器学习基础", top_k=10)
for result in results["results"]:
    print(f"Score: {result['score']}")
    print(f"Content: {result['content'][:100]}...")
    print("-" * 50)
```

---

## 集合管理

### 1. 列出所有集合

```bash
curl -X GET "http://localhost:8000/api/v1/collections" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应示例:**

```json
{
  "success": true,
  "message": "找到 3 个集合",
  "collections": [
    {
      "success": true,
      "name": "my_documents",
      "vectors_count": 1500,
      "points_count": 1500,
      "status": "green"
    },
    {
      "success": true,
      "name": "web_articles",
      "vectors_count": 320,
      "points_count": 320,
      "status": "green"
    }
  ],
  "total": 2,
  "timestamp": "2025-10-04T12:00:00Z"
}
```

### 2. 获取集合详细信息

```bash
curl -X GET "http://localhost:8000/api/v1/collections/my_documents/info" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. 删除集合

```bash
curl -X DELETE "http://localhost:8000/api/v1/collections/my_documents" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 健康检查

### 1. 健康检查

```bash
curl -X GET "http://localhost:8000/health"
```

**响应示例:**

```json
{
  "success": true,
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "timestamp": "2025-10-04T12:00:00Z",
  "dependencies": {
    "qdrant": {
      "status": "healthy",
      "latency_ms": 5.2,
      "details": {
        "collection": "documents",
        "vectors_count": 1500
      }
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.1
    }
  }
}
```

### 2. 就绪检查

```bash
curl -X GET "http://localhost:8000/ready"
```

### 3. Ping

```bash
curl -X GET "http://localhost:8000/ping"
```

---

## 完整工作流示例

### Python完整示例

```python
import requests
from typing import List, Dict

class DocumentAPI:
    """文档管理API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None

    def login(self, username: str, password: str):
        """登录获取令牌"""
        url = f"{self.base_url}/api/v1/auth/token"
        data = {"username": username, "password": password}
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        self.token = result["access_token"]
        return result

    def _get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def upload_file(self, file_path: str, collection: str = "documents"):
        """上传文件"""
        url = f"{self.base_url}/api/v1/documents/upload"
        headers = {"Authorization": f"Bearer {self.token}"}

        files = {"file": open(file_path, "rb")}
        data = {"collection_name": collection}

        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()

    def load_urls(self, urls: List[str], collection: str = "documents"):
        """从URL加载文档"""
        url = f"{self.base_url}/api/v1/documents/from-url"
        payload = {
            "urls": urls,
            "collection_name": collection
        }
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        return response.json()

    def search(self, query: str, collection: str = "documents", top_k: int = 5):
        """搜索文档"""
        url = f"{self.base_url}/api/v1/search"
        payload = {
            "query": query,
            "collection_name": collection,
            "top_k": top_k
        }
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        return response.json()

# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = DocumentAPI("http://localhost:8000")

    # 1. 登录
    client.login("admin", "admin123")
    print("✓ 登录成功")

    # 2. 上传文件
    result = client.upload_file("example.pdf", "my_docs")
    print(f"✓ 文件上传成功，生成 {result['total_chunks']} 个文档块")

    # 3. 加载URL
    urls = [
        "https://example.com/article1",
        "https://example.com/article2"
    ]
    result = client.load_urls(urls, "my_docs")
    print(f"✓ URL加载成功，加载 {result['urls_loaded']} 个网页")

    # 4. 搜索
    results = client.search("机器学习", "my_docs", top_k=5)
    print(f"✓ 搜索完成，找到 {results['total']} 个结果")

    for i, item in enumerate(results["results"], 1):
        print(f"\n结果 {i}:")
        print(f"  分数: {item.get('score', 'N/A')}")
        print(f"  内容: {item['content'][:100]}...")
```

---

## 错误处理

### 常见错误码

| 状态码 | 错误类型 | 说明 |
|-------|---------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或令牌无效 |
| 403 | Forbidden | 权限不足 |
| 413 | Payload Too Large | 文件过大 |
| 415 | Unsupported Media Type | 不支持的文件类型 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 超出速率限制 |
| 500 | Internal Server Error | 服务器内部错误 |

### 错误响应示例

```json
{
  "success": false,
  "message": "请求处理失败",
  "error_code": "VALIDATION_ERROR",
  "error_type": "RequestValidationError",
  "detail": "请求数据格式不正确",
  "errors": [
    {
      "loc": ["body", "chunk_size"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ],
  "timestamp": "2025-10-04T12:00:00Z"
}
```

---

## 速率限制

API实施了速率限制以保护服务：

- **默认限制**: 100次/分钟
- **文件上传**: 10次/分钟
- **搜索**: 50次/分钟

响应头中包含速率限制信息：

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638360000
```

---

## 性能优化建议

1. **批量操作**: 使用批量搜索API而不是多次单独搜索
2. **缓存**: 启用Redis缓存以提高响应速度
3. **分页**: 对大量结果使用适当的top_k值
4. **并发控制**: 避免过多并发请求
5. **压缩**: API自动支持Gzip压缩

---

## 更多信息

- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- Prometheus指标: http://localhost:8000/metrics
