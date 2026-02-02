#!/bin/bash

# GraphRAG Docker 快速启动脚本
# 使用方法: ./docker-run.sh [build|start|stop|restart|logs|clean]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_info "Docker 和 Docker Compose 已安装"
}

# 检查 .env 文件
check_env() {
    if [ ! -f .env ]; then
        print_warn ".env 文件不存在，从 .env.example 创建..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warn "请编辑 .env 文件并填入你的配置信息"
            print_warn "必填项: GRAPHRAG_API_KEY, Embedding_API_KEY"
            exit 1
        else
            print_error ".env.example 文件不存在"
            exit 1
        fi
    fi
    
    # 检查必需的环境变量
    source .env
    if [ -z "$GRAPHRAG_API_KEY" ] || [ "$GRAPHRAG_API_KEY" == "your-api-key-here" ]; then
        print_error "请在 .env 文件中设置 GRAPHRAG_API_KEY"
        exit 1
    fi
    
    if [ -z "$Embedding_API_KEY" ] || [ "$Embedding_API_KEY" == "your-embedding-api-key-here" ]; then
        print_error "请在 .env 文件中设置 Embedding_API_KEY"
        exit 1
    fi
    
    print_info "环境变量配置检查通过"
}

# 构建镜像
build() {
    print_info "开始构建 Docker 镜像..."
    docker-compose build --no-cache
    print_info "镜像构建完成"
}

# 启动服务
start() {
    check_env
    print_info "启动 GraphRAG 服务..."
    docker-compose up -d
    print_info "服务已启动"
    print_info "访问 http://localhost:8000 查看服务"
    print_info "访问 http://localhost:8000/docs 查看 API 文档"
    print_info "使用 './docker-run.sh logs' 查看日志"
}

# 停止服务
stop() {
    print_info "停止 GraphRAG 服务..."
    docker-compose down
    print_info "服务已停止"
}

# 重启服务
restart() {
    print_info "重启 GraphRAG 服务..."
    stop
    start
}

# 查看日志
logs() {
    print_info "查看服务日志 (Ctrl+C 退出)..."
    docker-compose logs -f
}

# 清理
clean() {
    print_warn "这将删除所有容器、镜像和卷，是否继续? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "清理 Docker 资源..."
        docker-compose down -v --rmi all
        print_info "清理完成"
    else
        print_info "取消清理"
    fi
}

# 显示状态
status() {
    print_info "服务状态:"
    docker-compose ps
    echo ""
    print_info "健康检查:"
    curl -s http://localhost:8000/api/health | python3 -m json.tool || print_error "服务未运行或健康检查失败"
}

# 显示帮助
show_help() {
    cat << EOF
GraphRAG Docker 管理脚本

使用方法:
    ./docker-run.sh [命令]

命令:
    build       构建 Docker 镜像
    start       启动服务
    stop        停止服务
    restart     重启服务
    logs        查看日志
    status      查看服务状态
    clean       清理所有 Docker 资源
    help        显示此帮助信息

示例:
    ./docker-run.sh build       # 构建镜像
    ./docker-run.sh start       # 启动服务
    ./docker-run.sh logs        # 查看日志
    ./docker-run.sh status      # 查看状态

注意:
    首次运行前请确保已配置 .env 文件
EOF
}

# 主函数
main() {
    check_docker
    
    case "${1:-help}" in
        build)
            build
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs
            ;;
        status)
            status
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
