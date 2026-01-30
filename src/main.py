"""
FastAPI 应用入口
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
import json
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from src.config import settings
from src.container import init_services
# from src.api.infrastructure import router as infrastructure_router
# from src.api.business import router as business_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化服务容器
init_services()


# 创建 FastAPI 应用
app = FastAPI(
    title="ASD地板时光干预辅助系统",
    description="基于Memory驱动的行为记录系统",
    version="1.0.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
# app.include_router(infrastructure_router)  # 暂不需要
# app.include_router(business_router)  # 暂不需要

# 注册行为观察路由
from src.api.observation import router as observation_router
app.include_router(observation_router)

# 注册游戏路由
from src.api.game import router as game_router
app.include_router(game_router)

# 注册评估路由
from src.api.assessment import router as assessment_router
app.include_router(assessment_router)

# 注册档案路由
from src.api.profile import router as profile_router
app.include_router(profile_router)

# 注册报告路由
from src.api.report import router as report_router
app.include_router(report_router)


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "message": "ASD地板时光干预辅助系统 API",
        "version": "1.0.0",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.post("/test/workflow")
async def test_workflow():
    """
    测试工作流（全 Mock）
    用于验证架构设计
    
    TODO: 待实现完整的 LangGraph 工作流
    """
    return {
        "status": "not_implemented",
        "message": "工作流功能待实现"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
    )
