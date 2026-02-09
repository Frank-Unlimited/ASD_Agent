#!/bin/bash

# 阿里云容器镜像服务推送脚本
# GraphRAG for Tutorial

set -e

# 阿里云镜像仓库配置
ALIYUN_REGISTRY="crpi-925djdtsud86yqkr.cn-hangzhou.personal.cr.aliyuncs.com"
ALIYUN_NAMESPACE="hhc510105200301150090"
ALIYUN_REPO="graphrag_for_tutorial"
ALIYUN_USERNAME="nick1329599640"

# VPC 内网地址（用于 ECS）
ALIYUN_REGISTRY_VPC="crpi-925djdtsud86yqkr-vpc.cn-hangzhou.personal.cr.aliyuncs.com"

# 本地镜像名称
LOCAL_IMAGE="graphrag-service"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 显示帮助
show_help() {
    cat << EOF
阿里云容器镜像服务推送脚本

使用方法:
    $0 [选项] <版本号>

选项:
    -v, --vpc       使用 VPC 内网地址（适用于 ECS）
    -h, --help      显示帮助信息

参数:
    版本号          镜像版本标签（如: v1.0.0, latest）

示例:
    $0 v1.0.0                    # 推送到公网地址
    $0 --vpc v1.0.0              # 推送到 VPC 内网地址
    $0 latest                    # 推送 latest 标签

注意:
    1. 首次使用需要先登录: docker login
    2. 确保本地已构建镜像: docker build -t graphrag-service .
    3. 密码为开通服务时设置的密码
EOF
}

# 登录阿里云镜像仓库
login_aliyun() {
    local registry=$1
    print_step "登录阿里云容器镜像服务..."
    print_info "Registry: $registry"
    print_info "Username: $ALIYUN_USERNAME"
    
    if docker login --username=$ALIYUN_USERNAME $registry; then
        print_info "登录成功"
    else
        print_error "登录失败"
        exit 1
    fi
}

# 构建本地镜像
build_image() {
    print_step "构建本地镜像..."
    
    if docker build -t $LOCAL_IMAGE:latest .; then
        print_info "镜像构建成功"
    else
        print_error "镜像构建失败"
        exit 1
    fi
}

# 标记镜像
tag_image() {
    local registry=$1
    local version=$2
    local remote_image="$registry/$ALIYUN_NAMESPACE/$ALIYUN_REPO:$version"
    
    print_step "标记镜像..."
    print_info "本地镜像: $LOCAL_IMAGE:latest"
    print_info "远程镜像: $remote_image"
    
    if docker tag $LOCAL_IMAGE:latest $remote_image; then
        print_info "镜像标记成功"
    else
        print_error "镜像标记失败"
        exit 1
    fi
    
    # 如果版本不是 latest，同时打上 latest 标签
    if [ "$version" != "latest" ]; then
        local latest_image="$registry/$ALIYUN_NAMESPACE/$ALIYUN_REPO:latest"
        print_info "同时标记为: $latest_image"
        docker tag $LOCAL_IMAGE:latest $latest_image
    fi
}

# 推送镜像
push_image() {
    local registry=$1
    local version=$2
    local remote_image="$registry/$ALIYUN_NAMESPACE/$ALIYUN_REPO:$version"
    
    print_step "推送镜像到阿里云..."
    print_info "推送: $remote_image"
    
    if docker push $remote_image; then
        print_info "镜像推送成功"
    else
        print_error "镜像推送失败"
        exit 1
    fi
    
    # 如果版本不是 latest，同时推送 latest 标签
    if [ "$version" != "latest" ]; then
        local latest_image="$registry/$ALIYUN_NAMESPACE/$ALIYUN_REPO:latest"
        print_info "推送: $latest_image"
        docker push $latest_image
    fi
}

# 显示拉取命令
show_pull_command() {
    local registry=$1
    local version=$2
    
    echo ""
    print_info "镜像推送完成！"
    echo ""
    echo "拉取命令:"
    echo "  docker pull $registry/$ALIYUN_NAMESPACE/$ALIYUN_REPO:$version"
    echo ""
    if [ "$version" != "latest" ]; then
        echo "或使用 latest 标签:"
        echo "  docker pull $registry/$ALIYUN_NAMESPACE/$ALIYUN_REPO:latest"
        echo ""
    fi
}

# 主函数
main() {
    local use_vpc=false
    local version=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--vpc)
                use_vpc=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                version=$1
                shift
                ;;
        esac
    done
    
    # 检查版本号
    if [ -z "$version" ]; then
        print_error "请指定版本号"
        echo ""
        show_help
        exit 1
    fi
    
    # 选择 Registry 地址
    local registry=$ALIYUN_REGISTRY
    if [ "$use_vpc" = true ]; then
        registry=$ALIYUN_REGISTRY_VPC
        print_info "使用 VPC 内网地址"
    else
        print_info "使用公网地址"
    fi
    
    echo ""
    print_info "=========================================="
    print_info "阿里云容器镜像推送"
    print_info "=========================================="
    print_info "仓库: $ALIYUN_NAMESPACE/$ALIYUN_REPO"
    print_info "版本: $version"
    print_info "Registry: $registry"
    print_info "=========================================="
    echo ""
    
    # 检查本地镜像是否存在
    if ! docker images | grep -q $LOCAL_IMAGE; then
        print_warn "本地镜像不存在，开始构建..."
        build_image
    else
        print_info "本地镜像已存在"
    fi
    
    # 登录
    login_aliyun $registry
    
    # 标记镜像
    tag_image $registry $version
    
    # 推送镜像
    push_image $registry $version
    
    # 显示拉取命令
    show_pull_command $registry $version
}

main "$@"
