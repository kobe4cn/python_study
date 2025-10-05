#!/bin/bash

# FastAPI应用启动脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  文档管理API - 启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查Python版本
echo -e "${YELLOW}检查Python版本...${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.11"

if ! python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo -e "${RED}❌ Python版本过低: $python_version${NC}"
    echo -e "${RED}   需要Python 3.11或更高版本${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python版本: $python_version${NC}"

# 检查虚拟环境
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠️  未在虚拟环境中运行${NC}"
    echo -e "${YELLOW}   建议创建虚拟环境: python -m venv venv${NC}"
    echo -e "${YELLOW}   激活虚拟环境: source venv/bin/activate${NC}"
    echo ""
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env文件不存在${NC}"
    echo -e "${YELLOW}   正在从.env.example复制...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env文件已创建${NC}"
    echo -e "${RED}⚠️  请编辑.env文件并配置必要的环境变量！${NC}"
    echo -e "${RED}   特别是: DASHSCOPE_API_KEY, SECRET_KEY${NC}"
    echo ""
fi

# 检查依赖
echo -e "${YELLOW}检查依赖...${NC}"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  依赖未安装${NC}"
    echo -e "${YELLOW}   正在安装依赖...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✓ 依赖已安装${NC}"
fi

# 创建必要的目录
echo -e "${YELLOW}创建必要的目录...${NC}"
mkdir -p uploads logs
echo -e "${GREEN}✓ 目录已创建${NC}"

# 检查Qdrant连接（可选）
echo -e "${YELLOW}检查Qdrant连接...${NC}"
if command -v curl &> /dev/null; then
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Qdrant服务正常${NC}"
    else
        echo -e "${RED}⚠️  无法连接到Qdrant (localhost:6333)${NC}"
        echo -e "${YELLOW}   请确保Qdrant服务已启动${NC}"
        echo -e "${YELLOW}   启动方式: docker run -p 6333:6333 qdrant/qdrant${NC}"
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  启动FastAPI服务器${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 启动模式选择
MODE=${1:-dev}

if [ "$MODE" = "dev" ]; then
    echo -e "${YELLOW}开发模式启动（热重载）${NC}"
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
elif [ "$MODE" = "prod" ]; then
    echo -e "${YELLOW}生产模式启动（多进程）${NC}"
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level warning
else
    echo -e "${RED}未知模式: $MODE${NC}"
    echo -e "${YELLOW}使用方法: ./run.sh [dev|prod]${NC}"
    exit 1
fi
