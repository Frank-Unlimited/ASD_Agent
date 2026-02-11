.PHONY: help build start stop restart logs status clean test shell

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## 显示帮助信息
	@echo "$(GREEN)GraphRAG Docker 管理命令$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)示例:$(NC)"
	@echo "  make build        # 构建 Docker 镜像"
	@echo "  make start        # 启动服务"
	@echo "  make logs         # 查看日志"

build: ## 构建 Docker 镜像
	@echo "$(GREEN)构建 Docker 镜像...$(NC)"
	docker-compose build

build-no-cache: ## 无缓存构建 Docker 镜像
	@echo "$(GREEN)无缓存构建 Docker 镜像...$(NC)"
	docker-compose build --no-cache

start: ## 启动服务
	@echo "$(GREEN)启动 GraphRAG 服务...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)服务已启动$(NC)"
	@echo "访问: http://localhost:8000"
	@echo "API 文档: http://localhost:8000/docs"

stop: ## 停止服务
	@echo "$(YELLOW)停止 GraphRAG 服务...$(NC)"
	docker-compose down

restart: stop start ## 重启服务

logs: ## 查看日志
	docker-compose logs -f

logs-tail: ## 查看最近 100 行日志
	docker-compose logs --tail=100

status: ## 查看服务状态
	@echo "$(GREEN)服务状态:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(GREEN)健康检查:$(NC)"
	@curl -s http://localhost:8000/api/health | python3 -m json.tool || echo "$(YELLOW)服务未运行$(NC)"

shell: ## 进入容器 shell
	docker-compose exec graphrag-service /bin/bash

test: ## 测试 API 连接
	@echo "$(GREEN)测试健康检查端点...$(NC)"
	@curl -s http://localhost:8000/api/health | python3 -m json.tool
	@echo ""
	@echo "$(GREEN)测试完成$(NC)"

clean: ## 清理容器和镜像
	@echo "$(YELLOW)清理 Docker 资源...$(NC)"
	docker-compose down -v --rmi all
	@echo "$(GREEN)清理完成$(NC)"

prune: ## 清理所有未使用的 Docker 资源
	@echo "$(YELLOW)清理未使用的 Docker 资源...$(NC)"
	docker system prune -af --volumes
	@echo "$(GREEN)清理完成$(NC)"

env-check: ## 检查环境变量配置
	@echo "$(GREEN)检查环境变量配置...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW).env 文件不存在，从 .env.example 创建...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)请编辑 .env 文件并填入配置$(NC)"; \
	else \
		echo "$(GREEN).env 文件存在$(NC)"; \
	fi

env-show: ## 显示当前环境变量配置（隐藏敏感信息）
	@echo "$(GREEN)当前环境变量配置:$(NC)"
	@docker-compose config | grep -E "GRAPHRAG|Embedding|IMAGE|TABLE|MINERU|PDF" | sed 's/\(API_KEY.*:\).*/\1 ***HIDDEN***/'

up: start ## 启动服务（别名）

down: stop ## 停止服务（别名）

ps: status ## 查看状态（别名）

rebuild: ## 重新构建并启动
	@echo "$(GREEN)重新构建并启动服务...$(NC)"
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "$(GREEN)服务已重新启动$(NC)"

dev: ## 开发模式启动（显示日志）
	@echo "$(GREEN)开发模式启动...$(NC)"
	docker-compose up

prod: ## 生产模式启动
	@echo "$(GREEN)生产模式启动...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)服务已在后台启动$(NC)"

backup-data: ## 备份数据目录
	@echo "$(GREEN)备份数据目录...$(NC)"
	@tar -czf backup-data-$$(date +%Y%m%d-%H%M%S).tar.gz data/ output/
	@echo "$(GREEN)备份完成$(NC)"

install: env-check build start ## 完整安装流程
	@echo "$(GREEN)安装完成！$(NC)"
	@echo "访问: http://localhost:8000"

# 阿里云镜像推送
aliyun-login: ## 登录阿里云镜像仓库
	@echo "$(GREEN)登录阿里云容器镜像服务...$(NC)"
	docker login --username=nick1329599640 crpi-925djdtsud86yqkr.cn-hangzhou.personal.cr.aliyuncs.com

aliyun-push: ## 推送镜像到阿里云（使用: make aliyun-push VERSION=v1.0.0）
	@if [ -z "$(VERSION)" ]; then \
		echo "$(RED)错误: 请指定版本号$(NC)"; \
		echo "使用方法: make aliyun-push VERSION=v1.0.0"; \
		exit 1; \
	fi
	@echo "$(GREEN)推送镜像到阿里云...$(NC)"
	./aliyun-docker-push.sh $(VERSION)

aliyun-push-vpc: ## 推送镜像到阿里云 VPC（使用: make aliyun-push-vpc VERSION=v1.0.0）
	@if [ -z "$(VERSION)" ]; then \
		echo "$(RED)错误: 请指定版本号$(NC)"; \
		echo "使用方法: make aliyun-push-vpc VERSION=v1.0.0"; \
		exit 1; \
	fi
	@echo "$(GREEN)推送镜像到阿里云 VPC...$(NC)"
	./aliyun-docker-push.sh --vpc $(VERSION)

aliyun-pull: ## 从阿里云拉取镜像（使用: make aliyun-pull VERSION=v1.0.0）
	@if [ -z "$(VERSION)" ]; then \
		VERSION=latest; \
	fi
	@echo "$(GREEN)从阿里云拉取镜像...$(NC)"
	docker pull crpi-925djdtsud86yqkr.cn-hangzhou.personal.cr.aliyuncs.com/hhc510105200301150090/graphrag_for_tutorial:$$VERSION
