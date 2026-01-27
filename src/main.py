"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.container import init_services
from src.langgraph import get_compiled_workflow
from src.models.state import DynamicInterventionState
from src.api.workflow import router as workflow_router
from src.api.infrastructure import router as infrastructure_router
from src.api.business import router as business_router

# 初始化服务容器
init_services()

# 创建 FastAPI 应用
app = FastAPI(
    title="ASD地板时光干预辅助系统",
    description="基于LangGraph的多Agent协同干预系统",
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
