"""
快速启动脚本
"""
import uvicorn
from src.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("ASD地板时光干预辅助系统 - 后端服务")
    print("=" * 60)
    print(f"环境: {settings.environment}")
    print(f"端口: {settings.port}")
    print(f"使用 Mock 服务: 是")
    print("=" * 60)
    print("\n启动服务中...\n")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
    )
