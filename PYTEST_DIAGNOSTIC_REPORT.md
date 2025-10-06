# Pytest 测试失败诊断报告

## 问题摘要

测试执行时遇到退出码 2，经诊断发现是 pytest 配置问题导致的。

## 根本原因分析

### 1. 主要问题：pytest-cov 插件未安装

**错误信息：**
```
pytest: error: unrecognized arguments: --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml --cov-config=.coveragerc
```

**根本原因：**
- `pytest.ini` 配置文件中启用了 coverage 相关选项
- 但虚拟环境中未安装 `pytest-cov` 插件
- pytest 无法识别 `--cov` 等参数，导致初始化失败，退出码为 2

**诊断过程：**
1. 检查 Python 版本：Python 3.13.7
2. 检查虚拟环境：`.venv` 存在
3. 检查 pytest 版本：8.4.2 (已安装)
4. 检查 pytest-cov：未安装 ❌
5. 确认 pytest.ini 中包含 coverage 配置

### 2. 次要问题：测试依赖缺失

**缺失的依赖：**
- `pytest-cov` - 代码覆盖率插件
- `pytest-asyncio` - 异步测试支持
- `pytest-mock` - Mock 工具
- `pytest-timeout` - 测试超时控制

### 3. 环境问题

**Docker 容器状态：**
- Docker 命令不可用（可能未安装或未启动）
- Qdrant 容器状态未知
- 部分集成测试可能需要 Qdrant 运行

## 解决方案

### 方案 1：安装完整测试依赖（推荐）

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 安装测试依赖
pip install -r requirements-test.txt

# 3. 运行测试
pytest
```

**requirements-test.txt** 已创建，包含：
```
# 测试依赖
pytest>=7.0
pytest-cov>=4.0
pytest-asyncio>=0.21.0
pytest-mock>=3.11.0
pytest-timeout>=2.1.0

# 代码质量工具
ruff>=0.1.0
mypy>=1.0
bandit>=1.7.5

# 类型存根
types-python-jose
types-passlib
types-redis
types-requests
```

### 方案 2：禁用 Coverage（快速修复）

已更新 `pytest.ini`，将 coverage 选项注释掉：

```ini
addopts =
    -ra
    --strict-markers
    --strict-config
    --showlocals
    --tb=short
# Coverage 选项已移至 pyproject.toml
# 如需启用 coverage，请先安装: pip install pytest-cov
# 然后取消下面几行的注释:
#    --cov=.
#    --cov-report=term-missing
#    --cov-report=html
#    --cov-report=xml
```

**验证结果：**
- ✅ 测试收集成功：69 个测试用例
- ✅ 配置测试通过：18/18 passed
- ✅ 整体测试：61 passed, 8 failed

### 方案 3：环境检查脚本

已创建 `scripts/check-services.sh` 用于检查测试依赖：

```bash
# 运行环境检查
bash scripts/check-services.sh
```

**检查项目：**
1. Docker 是否安装
2. Qdrant 容器是否运行
3. 环境变量配置（.env）
4. Python 虚拟环境
5. pytest 及相关插件

## 当前测试状态

### 成功的测试（61个）
- ✅ 配置测试：18/18
- ✅ 容器测试：部分通过
- ✅ 文档加载测试：通过
- ✅ Markdown 分割测试：通过
- ✅ 向量存储测试：部分通过

### 失败的测试（8个）

#### 1. test_container.py::test_get_llm_default
- **原因：** `.env` 文件缺少必需的环境变量
- **修复：** 配置 `LLM_API_KEY` 等环境变量

#### 2. test_llm_registry.py::test_qwen_provider_registration
- **原因：** LLM API 密钥未配置
- **修复：** 设置有效的 API 密钥

#### 3-8. test_vstore_main.py (6个失败)
- **原因：** Mock 路径错误 - `QdrantVectorStoreClient` 导入问题
- **修复：** 需要检查 `vstore_main.py` 的导入语句

## 修复步骤

### 立即修复（消除退出码 2）

```bash
# 方法 1：安装 pytest-cov
source .venv/bin/activate
pip install pytest-cov

# 方法 2：使用已修复的配置
# pytest.ini 已更新，coverage 选项已注释
pytest  # 现在可以正常运行
```

### 完整修复（通过所有测试）

```bash
# 1. 安装测试依赖
source .venv/bin/activate
pip install -r requirements-test.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入真实的 API 密钥

# 3. 启动 Qdrant（如需运行集成测试）
docker run -d -p 6333:6333 -p 6334:6334 \
  --name qdrant \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# 4. 运行测试
pytest -v                    # 详细输出
pytest -m unit              # 只运行单元测试
pytest -m integration       # 只运行集成测试
```

## 测试命令参考

```bash
# 基础命令
pytest                                    # 运行所有测试
pytest -v                                # 详细输出
pytest -x                                # 遇到第一个失败停止
pytest --lf                              # 只运行上次失败的测试

# 按标记运行
pytest -m unit                           # 只运行单元测试
pytest -m integration                    # 只运行集成测试
pytest -m "not integration"              # 跳过集成测试

# 按文件/目录运行
pytest tests/test_config.py             # 运行特定文件
pytest tests/test_config.py::TestLLMSettings  # 运行特定类
pytest tests/                            # 运行整个目录

# 启用 Coverage（需要先安装 pytest-cov）
pytest --cov=. --cov-report=html        # 生成 HTML 报告
pytest --cov=. --cov-report=term-missing # 显示缺失覆盖的行
```

## 预防措施

### 1. 依赖管理
- 将测试依赖与运行依赖分离
- 使用 `requirements-test.txt` 管理测试依赖
- CI/CD 中确保安装测试依赖

### 2. 环境检查
- 使用 `scripts/check-services.sh` 进行测试前检查
- 在 CI 中添加环境验证步骤
- 提供 `.env.example` 模板

### 3. 配置文件
- pytest.ini：基础配置，不依赖可选插件
- pyproject.toml：工具配置集中管理
- 可选功能使用注释说明如何启用

### 4. 文档说明
- README 中添加测试运行说明
- 说明可选依赖的安装方法
- 提供常见问题的解决方案

## 相关文件

**已创建/修改的文件：**
- ✅ `/Users/kevin/dev/ai/homework/requirements-test.txt` - 测试依赖配置
- ✅ `/Users/kevin/dev/ai/homework/pytest.ini` - pytest 配置（已修复）
- ✅ `/Users/kevin/dev/ai/homework/scripts/check-services.sh` - 环境检查脚本

**需要检查的文件：**
- `/Users/kevin/dev/ai/homework/.env` - 环境变量配置
- `/Users/kevin/dev/ai/homework/doc/vstore/vstore_main.py` - 导入问题
- `/Users/kevin/dev/ai/homework/tests/test_vstore_main.py` - Mock 路径修复

## 总结

### 问题定性
- **严重程度：** 中等
- **影响范围：** 所有测试无法运行（退出码 2）
- **修复难度：** 简单（配置问题）

### 根本原因
- pytest-cov 插件未安装，但配置中启用了 coverage
- 测试依赖未在 requirements.txt 中明确声明

### 解决状态
- ✅ pytest 配置已修复（移除 coverage 依赖）
- ✅ 测试依赖配置文件已创建
- ✅ 环境检查脚本已提供
- ✅ 测试现可正常运行（61/69 通过）
- ⏳ 剩余 8 个测试失败需要代码层面修复（非配置问题）

### 下一步建议
1. 安装 `requirements-test.txt` 中的依赖
2. 配置 `.env` 环境变量
3. 修复 test_vstore_main.py 中的 Mock 问题
4. 启动 Qdrant 容器运行集成测试
5. 启用 coverage 生成测试覆盖率报告
