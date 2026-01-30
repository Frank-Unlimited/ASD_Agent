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
from src.workflow import get_compiled_workflow
from src.models.state import DynamicInterventionState
from src.api.workflow import router as workflow_router
from src.api.infrastructure import router as infrastructure_router
from src.api.business import router as business_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化服务容器
init_services()


# 请求日志中间件
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始
        start_time = time.time()
        request_id = f"{int(start_time * 1000)}"
        
        # 读取请求体（如果有）
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode('utf-8')
                    # 重新设置 body 以便后续处理
                    async def receive():
                        return {"type": "http.request", "body": body_bytes}
                    request._receive = receive
            except Exception as e:
                print(f"[警告] 无法读取请求体: {e}")
        
        # 记录请求信息
        print(f"\n{'='*80}")
        print(f"[请求 {request_id}] {request.method} {request.url.path}")
        if body:
            try:
                body_json = json.loads(body)
                print(f"[请求体] {json.dumps(body_json, ensure_ascii=False, indent=2)}")
            except:
                print(f"[请求体] {body[:200]}...")
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算耗时
            duration = time.time() - start_time
            
            # 记录响应信息
            print(f"[响应] 状态码: {response.status_code} | 耗时: {duration:.3f}s")
            print(f"{'='*80}\n")
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"[错误] {str(e)} | 耗时: {duration:.3f}s")
    


# 创建 FastAPI 应用
app = FastAPI(
    title="ASD地板时光干预辅助系统",
    description="基于LangGraph的多Agent协同干预系统",
    version="1.0.0",
)

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(workflow_router)
app.include_router(infrastructure_router)
app.include_router(business_router)


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
    """
    # 创建初始 State
    initial_state: DynamicInterventionState = {
        "childTimeline": {
            "profile": {
                "childId": "child-001",
                "name": "辰辰",
                "age": 2.5,
                "birthDate": "2023-07-01",
                "diagnosis": "ASD轻度",
                "interests": ["旋转物体", "水流"],
                "customDimensions": {}
            },
            "metrics": {},
            "microObservations": []
        },
        "currentContext": {
            "recentTrends": {},
            "attentionPoints": [],
            "activeGoals": [],
            "lastUpdated": None
        },
        "currentSession": {},
        "currentWeeklyPlan": None,
        "sessionHistory": None,
        "conversationHistory": None,
        "workflow": {
            "currentNode": "start",
            "nextNode": None,
            "isHITLPaused": False,
            "checkpointId": None,
            "needsAdjustment": None
        },
        "tempData": {
            "reportPath": "/mock/report.pdf",
            "gameId": "game-001"
        }
    }
    
    # 获取编译后的工作流
    workflow = get_compiled_workflow()
    
    # 执行工作流（简化版，不包含 HITL 暂停）
    try:
        # 注意：这里简化了 HITL 暂停的处理
        # 实际应用中需要使用 Checkpoint 机制
        result = await workflow.ainvoke(initial_state)
        
        return {
            "status": "success",
            "message": "工作流执行完成（Mock 数据）",
            "result": {
                "childId": result['childTimeline']['profile']['childId'],
                "currentNode": result['workflow']['currentNode'],
                "sessionId": result.get('currentSession', {}).get('sessionId'),
                "weeklyPlanId": result.get('currentWeeklyPlan', {}).get('planId')
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"工作流执行失败: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
    )
