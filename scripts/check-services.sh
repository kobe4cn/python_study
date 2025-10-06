#!/bin/bash
# 服务依赖检查脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔍 检查测试所需服务..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker 未安装${NC}"
        echo "  请访问 https://www.docker.com/get-started 安装 Docker"
        return 1
    fi
    echo -e "${GREEN}✓ Docker 已安装${NC}"
    return 0
}

# 检查 Qdrant 容器
check_qdrant() {
    echo ""
    echo "检查 Qdrant 向量数据库..."

    if ! docker ps --format '{{.Names}}' | grep -q "qdrant"; then
        echo -e "${YELLOW}⚠ Qdrant 容器未运行${NC}"
        echo ""
        echo "启动 Qdrant 容器的命令:"
        echo "  docker run -d -p 6333:6333 -p 6334:6334 \\"
        echo "    --name qdrant \\"
        echo "    -v \$(pwd)/qdrant_storage:/qdrant/storage \\"
        echo "    qdrant/qdrant:latest"
        echo ""
        read -p "是否现在启动 Qdrant? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker run -d -p 6333:6333 -p 6334:6334 \
                --name qdrant \
                -v "${PROJECT_ROOT}/qdrant_storage:/qdrant/storage" \
                qdrant/qdrant:latest

            echo -e "${GREEN}✓ Qdrant 容器已启动${NC}"
            echo "等待 Qdrant 完全启动..."
            sleep 5
        else
            echo -e "${YELLOW}跳过 Qdrant 启动 (部分集成测试可能失败)${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}✓ Qdrant 容器运行中${NC}"
        docker ps --filter "name=qdrant" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    fi

    # 检查 Qdrant 健康状态
    echo ""
    echo "检查 Qdrant 健康状态..."
    if curl -s http://localhost:6333/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Qdrant 健康检查通过${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Qdrant 健康检查失败 (容器可能仍在启动中)${NC}"
        return 1
    fi
}

# 检查环境变量
check_env() {
    echo ""
    echo "检查环境配置..."

    if [ ! -f "${PROJECT_ROOT}/.env" ]; then
        echo -e "${YELLOW}⚠ .env 文件不存在${NC}"
        if [ -f "${PROJECT_ROOT}/.env.example" ]; then
            echo "  建议复制 .env.example 为 .env 并配置相关参数"
            echo "  cp .env.example .env"
        fi
        return 1
    fi
    echo -e "${GREEN}✓ .env 文件存在${NC}"

    # 检查关键环境变量
    source "${PROJECT_ROOT}/.env"

    if [ -z "$LLM_API_KEY" ] || [ "$LLM_API_KEY" == "your-api-key-here" ]; then
        echo -e "${YELLOW}⚠ LLM_API_KEY 未配置${NC}"
    else
        echo -e "${GREEN}✓ LLM_API_KEY 已配置${NC}"
    fi

    return 0
}

# 检查 Python 虚拟环境
check_venv() {
    echo ""
    echo "检查 Python 虚拟环境..."

    if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
        echo -e "${RED}✗ 虚拟环境不存在${NC}"
        echo "  创建虚拟环境: python3 -m venv .venv"
        return 1
    fi
    echo -e "${GREEN}✓ 虚拟环境存在${NC}"

    # 激活虚拟环境并检查 pytest
    source "${PROJECT_ROOT}/.venv/bin/activate"

    if ! python -c "import pytest" 2>/dev/null; then
        echo -e "${YELLOW}⚠ pytest 未安装${NC}"
        echo "  安装测试依赖: pip install -r requirements-test.txt"
        return 1
    fi

    PYTEST_VERSION=$(python -c "import pytest; print(pytest.__version__)")
    echo -e "${GREEN}✓ pytest ${PYTEST_VERSION} 已安装${NC}"

    # 检查 pytest-cov
    if ! python -c "import pytest_cov" 2>/dev/null; then
        echo -e "${YELLOW}⚠ pytest-cov 未安装 (coverage 报告将不可用)${NC}"
        echo "  安装: pip install pytest-cov"
    else
        echo -e "${GREEN}✓ pytest-cov 已安装${NC}"
    fi

    deactivate
    return 0
}

# 主检查流程
main() {
    echo "========================================"
    echo "  测试环境依赖检查"
    echo "========================================"

    ISSUES=0

    check_docker || ((ISSUES++))

    if command -v docker &> /dev/null; then
        check_qdrant || ((ISSUES++))
    fi

    check_env || ((ISSUES++))
    check_venv || ((ISSUES++))

    echo ""
    echo "========================================"
    if [ $ISSUES -eq 0 ]; then
        echo -e "${GREEN}✓ 所有检查通过，可以运行测试${NC}"
        echo ""
        echo "运行测试的命令:"
        echo "  source .venv/bin/activate"
        echo "  pytest                          # 运行所有测试"
        echo "  pytest -v                       # 详细输出"
        echo "  pytest -m unit                  # 只运行单元测试"
        echo "  pytest -m integration           # 只运行集成测试"
        exit 0
    else
        echo -e "${YELLOW}⚠ 发现 ${ISSUES} 个问题需要解决${NC}"
        echo ""
        echo "修复建议:"
        echo "  1. 安装缺失的依赖"
        echo "  2. 启动所需的服务"
        echo "  3. 配置环境变量"
        echo "  4. 重新运行此检查脚本"
        exit 1
    fi
}

main "$@"
