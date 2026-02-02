#!/bin/bash

# Docker 配置测试脚本

set -e

echo "🔍 测试 Docker 配置..."
echo ""

# 1. 检查 Docker
echo "1️⃣ 检查 Docker 安装..."
docker --version
docker-compose --version
echo "✅ Docker 已安装"
echo ""

# 2. 验证 docker-compose.yml
echo "2️⃣ 验证 docker-compose.yml 语法..."
docker-compose config --quiet && echo "✅ docker-compose.yml 语法正确" || echo "❌ docker-compose.yml 语法错误"
echo ""

# 3. 检查 Dockerfile
echo "3️⃣ 检查 Dockerfile..."
if [ -f Dockerfile ]; then
    echo "✅ Dockerfile 存在"
else
    echo "❌ Dockerfile 不存在"
    exit 1
fi
echo ""

# 4. 检查 .dockerignore
echo "4️⃣ 检查 .dockerignore..."
if [ -f .dockerignore ]; then
    echo "✅ .dockerignore 存在"
else
    echo "⚠️  .dockerignore 不存在（建议创建）"
fi
echo ""

# 5. 检查环境变量文件
echo "5️⃣ 检查环境变量配置..."
if [ -f .env.example ]; then
    echo "✅ .env.example 存在"
else
    echo "❌ .env.example 不存在"
fi

if [ -f .env ]; then
    echo "✅ .env 存在"
    # 检查必需的变量
    if grep -q "GRAPHRAG_API_KEY=your-api-key-here" .env; then
        echo "⚠️  请在 .env 中设置 GRAPHRAG_API_KEY"
    fi
    if grep -q "Embedding_API_KEY=your-embedding-api-key-here" .env; then
        echo "⚠️  请在 .env 中设置 Embedding_API_KEY"
    fi
else
    echo "⚠️  .env 不存在（将使用默认值）"
fi
echo ""

# 6. 检查必需的目录
echo "6️⃣ 检查必需的目录..."
for dir in data output server graphrag; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/ 目录存在"
    else
        echo "❌ $dir/ 目录不存在"
    fi
done
echo ""

# 7. 检查 pyproject.toml
echo "7️⃣ 检查 pyproject.toml..."
if [ -f pyproject.toml ]; then
    echo "✅ pyproject.toml 存在"
else
    echo "❌ pyproject.toml 不存在"
    exit 1
fi
echo ""

echo "✨ 配置检查完成！"
echo ""
echo "📝 下一步："
echo "   1. 确保 .env 文件已正确配置"
echo "   2. 运行 'make build' 或 './docker-run.sh build' 构建镜像"
echo "   3. 运行 'make start' 或 './docker-run.sh start' 启动服务"
echo ""
