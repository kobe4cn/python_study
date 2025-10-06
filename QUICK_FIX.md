# Pytest 退出码 2 - 快速修复指南

## 问题：pytest 退出码 2

```
pytest: error: unrecognized arguments: --cov=. --cov-report=term-missing
```

## 原因

pytest-cov 插件未安装，但 pytest.ini 配置中使用了 `--cov` 参数。

## 快速解决方案

### 选项 1：安装 pytest-cov（推荐）

```bash
source .venv/bin/activate
pip install pytest-cov
pytest
```

### 选项 2：使用已修复的配置

```bash
# pytest.ini 已更新，coverage 选项已被注释
source .venv/bin/activate
pytest
```

### 选项 3：临时覆盖配置

```bash
source .venv/bin/activate
pytest -o addopts="-ra --strict-markers --strict-config --showlocals --tb=short"
```

## 安装完整测试依赖

```bash
source .venv/bin/activate
pip install -r requirements-test.txt
```

## 验证修复

```bash
# 应该看到类似输出：
# ===== test session starts =====
# collected 69 items
# ...
# ===== 61 passed, 8 failed in 2.35s =====

pytest -v
```

## 当前测试状态

- ✅ 配置问题已修复
- ✅ 61/69 测试通过
- ⚠️ 8 个测试失败（非配置问题，是代码问题）

## 失败的测试原因

1. **容器测试**：`.env` 缺少环境变量
2. **LLM 测试**：API 密钥未配置
3. **向量存储测试**：Mock 路径问题

## 完整修复步骤

```bash
# 1. 安装依赖
source .venv/bin/activate
pip install -r requirements-test.txt

# 2. 配置环境
cp .env.example .env
# 编辑 .env 设置 LLM_API_KEY

# 3. 启动 Qdrant（可选）
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest

# 4. 运行测试
pytest -v
```

## 运行环境检查

```bash
bash scripts/check-services.sh
```

## 常用测试命令

```bash
# 只运行单元测试（不需要外部服务）
pytest -m unit

# 跳过集成测试
pytest -m "not integration"

# 运行特定文件
pytest tests/test_config.py -v

# 查看详细错误
pytest -vv --tb=long
```

---

详细诊断报告：[PYTEST_DIAGNOSTIC_REPORT.md](./PYTEST_DIAGNOSTIC_REPORT.md)
