# 测试修复清单

## 已修复问题 ✅

### 1. Pytest 退出码 2 - 配置问题
- **问题：** pytest-cov 未安装但配置中使用了 coverage 参数
- **修复：** 更新 pytest.ini，注释掉 coverage 相关配置
- **文件：** `/Users/kevin/dev/ai/homework/pytest.ini`
- **状态：** ✅ 已完成

### 2. 测试依赖缺失
- **问题：** 测试相关依赖未明确声明
- **修复：** 创建 requirements-test.txt
- **文件：** `/Users/kevin/dev/ai/homework/requirements-test.txt`
- **状态：** ✅ 已完成

### 3. 环境检查工具
- **问题：** 缺少测试前环境验证
- **修复：** 创建服务检查脚本
- **文件：** `/Users/kevin/dev/ai/homework/scripts/check-services.sh`
- **状态：** ✅ 已完成

## 待修复测试问题 ⏳

### 1. test_vstore_main.py - Mock 导入问题 (6个测试失败)

#### 问题分析
```python
# 测试中的 Mock 路径
@patch('doc.vstore.vstore_main.QdrantVectorStoreClient')

# 实际代码中的导入方式（在方法内部动态导入）
def _initialize_vstore(self) -> BaseVectorStore:
    match self.config.provider:
        case VectorStoreProvider.QDRANT:
            from doc.vstore.qdrant_vector_store_client import QdrantVectorStoreClient
            return QdrantVectorStoreClient(...)
```

**根本原因：** `QdrantVectorStoreClient` 在运行时动态导入，不在模块顶层，Mock 路径无法定位。

#### 失败的测试
1. `test_config_validation` - AttributeError
2. `test_valid_collection_names` - AttributeError
3. `test_add_documents_empty_list` - AttributeError
4. `test_search_empty_query` - AttributeError
5. `test_context_manager` - AttributeError
6. `test_lazy_loading` - AttributeError

#### 解决方案

**方案 A：修改 Mock 路径（推荐）**

```python
# 在 tests/test_vstore_main.py 中
# 将所有 Mock 从这个路径：
@patch('doc.vstore.vstore_main.QdrantVectorStoreClient')

# 改为实际导入路径：
@patch('doc.vstore.qdrant_vector_store_client.QdrantVectorStoreClient')
```

**方案 B：修改源代码导入方式**

```python
# 在 doc/vstore/vstore_main.py 顶部添加
from doc.vstore.qdrant_vector_store_client import QdrantVectorStoreClient

# 然后在 _initialize_vstore 中直接使用
case VectorStoreProvider.QDRANT:
    return QdrantVectorStoreClient(...)
```

**方案 C：使用 Mock 对象而不是 patch**

```python
def test_lazy_loading(self):
    # 创建 Mock 实例
    mock_client = Mock(spec=BaseVectorStore)

    with patch.object(
        VStoreMain,
        '_initialize_vstore',
        return_value=mock_client
    ):
        vstore = VStoreMain(...)
        _ = vstore.vstore
        # 验证懒加载行为
```

**推荐：方案 A - 修改 Mock 路径**

修改文件：`/Users/kevin/dev/ai/homework/tests/test_vstore_main.py`

```python
# 修改所有相关测试
@patch('doc.vstore.qdrant_vector_store_client.QdrantVectorStoreClient')
def test_add_documents_empty_list(self, MockClient):
    # ... 测试代码保持不变

@patch('doc.vstore.qdrant_vector_store_client.QdrantVectorStoreClient')
def test_search_empty_query(self, MockClient):
    # ... 测试代码保持不变

# 等等...
```

### 2. test_container.py - 环境变量缺失

#### 问题
```
Failed: DID NOT RAISE <class 'ValueError'>
```

测试期望在缺少环境变量时抛出 ValueError，但实际上容器使用了默认值。

#### 失败的测试
- `test_get_llm_default`

#### 解决方案

检查并更新 `.env` 文件：

```bash
# 方法 1：复制示例文件
cp .env.example .env

# 方法 2：设置必需的环境变量
cat >> .env << 'EOF'
LLM_PROVIDER=qwen
LLM_MODEL=qwen3-max
LLM_API_KEY=your-test-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EOF
```

或者修改测试，使其正确处理默认值情况。

### 3. test_llm_registry.py - API 密钥验证

#### 问题
```
Expected 'qwen' in registry after registration
```

LLM 注册可能因为 API 密钥验证失败而未成功。

#### 失败的测试
- `test_qwen_provider_registration`

#### 解决方案

1. **配置有效的 API 密钥：**
   ```bash
   # 在 .env 中设置
   LLM_API_KEY=sk-your-actual-api-key
   ```

2. **或修改测试使用 Mock：**
   ```python
   @patch('llm.providers.qwen.QwenClient')
   def test_qwen_provider_registration(self, mock_client):
       # 使用 Mock 避免真实 API 调用
       ...
   ```

## 修复优先级

### 高优先级 🔴
1. **修复 test_vstore_main.py Mock 路径** (影响 6 个测试)
   - 文件：`/Users/kevin/dev/ai/homework/tests/test_vstore_main.py`
   - 预计时间：10 分钟
   - 难度：简单

### 中优先级 🟡
2. **配置 .env 环境变量** (影响 2 个测试)
   - 文件：`/Users/kevin/dev/ai/homework/.env`
   - 预计时间：5 分钟
   - 难度：简单

### 低优先级 🟢
3. **Qdrant 集成测试**
   - 需要：Docker + Qdrant 容器
   - 可选：仅影响集成测试
   - 预计时间：5 分钟

## 快速修复命令

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 修复 test_vstore_main.py
# 使用编辑器将所有
#   @patch('doc.vstore.vstore_main.QdrantVectorStoreClient')
# 替换为
#   @patch('doc.vstore.qdrant_vector_store_client.QdrantVectorStoreClient')

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 设置 LLM_API_KEY

# 4. 运行测试验证
pytest tests/test_vstore_main.py -v
pytest tests/test_container.py -v
pytest tests/test_llm_registry.py -v

# 5. 运行所有测试
pytest -v
```

## 修复后的预期结果

修复所有问题后，应该看到：

```
===== test session starts =====
...
===== 69 passed in X.XXs =====
```

## 可选：启用 Coverage

```bash
# 1. 安装 pytest-cov
pip install pytest-cov

# 2. 取消 pytest.ini 中 coverage 选项的注释

# 3. 运行带覆盖率的测试
pytest --cov=. --cov-report=html --cov-report=term-missing

# 4. 查看 HTML 报告
open htmlcov/index.html
```

## 验证清单

- [ ] pytest 可以正常收集测试（无退出码 2）
- [ ] test_vstore_main.py 所有测试通过
- [ ] test_container.py 所有测试通过
- [ ] test_llm_registry.py 所有测试通过
- [ ] 所有 69 个测试通过
- [ ] （可选）启用 coverage 并生成报告
- [ ] （可选）Qdrant 容器运行用于集成测试

## 相关文档

- [PYTEST_DIAGNOSTIC_REPORT.md](./PYTEST_DIAGNOSTIC_REPORT.md) - 详细诊断报告
- [QUICK_FIX.md](./QUICK_FIX.md) - 快速修复指南
- [requirements-test.txt](./requirements-test.txt) - 测试依赖
- [scripts/check-services.sh](./scripts/check-services.sh) - 环境检查脚本
