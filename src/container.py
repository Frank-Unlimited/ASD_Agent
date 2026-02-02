"""
依赖注入容器
管理所有服务实例，支持 Mock/Real 切换
"""
from typing import Dict, Any, Type
from src.config import settings


class ServiceContainer:
    """服务容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
    
    def register(self, name: str, service: Any) -> None:
        """注册服务"""
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """获取服务"""
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found in container")
        return self._services[name]
    
    def has(self, name: str) -> bool:
        """检查服务是否存在"""
        return name in self._services


# 全局容器实例
container = ServiceContainer()


def init_services():
    """
    初始化所有服务
    只初始化已实现的核心服务
    """
    print("[Container] 开始初始化服务...")
    
    # 游戏知识库（库内预设游戏）
    try:
        from services.game.library_service import GameLibraryService
        container.register('game_library', GameLibraryService())
        print("[Container] ✅ 游戏库服务已注册")
    except Exception as e:
        print(f"[Container] ⚠️ 游戏库服务注册失败: {e}")

    # SQLite 服务（始终使用真实实现）
    try:
        from services.SQLite.service import SQLiteService
        sqlite_service = SQLiteService()
        container.register('sqlite', sqlite_service)
        print("[Container] ✅ SQLite 服务已注册")
    except Exception as e:
        print(f"[Container] ⚠️ SQLite 服务注册失败: {e}")
    
    # 文件上传服务（始终使用真实实现）
    try:
        from services.FileUpload.service import FileUploadService
        container.register('file_upload', FileUploadService())
        print("[Container] ✅ 文件上传服务已注册")
    except Exception as e:
        print(f"[Container] ⚠️ 文件上传服务注册失败: {e}")
    
    # LLM 服务（根据配置动态加载）
    try:
        from services.LLM_Service.service import get_llm_service
        llm = get_llm_service()
        container.register('llm', llm)
        print(f"[Container] ✅ LLM 服务已注册: {settings.llm_model}")
    except Exception as e:
        print(f"[Container] ⚠️ LLM 服务注册失败: {e}")

    # 业务服务：行为观察服务（依赖 Memory 服务）
    # Memory 服务延迟初始化，在第一次请求时创建
    try:
        from services.observation import ObservationService
        
        # 创建一个占位服务，实际的 memory_service 会在第一次使用时初始化
        observation_service = ObservationService(
            memory_service=None,  # 延迟初始化
            speech_service=None
        )
        container.register('observation', observation_service)
        print("[Container] ✅ 行为观察服务已注册（Memory 延迟初始化）")
    except Exception as e:
        print(f"[Container] ⚠️ 行为观察服务注册失败: {e}")

    # 业务服务：游戏推荐服务（依赖 SQLite + Memory）
    try:
        from services.game import GameRecommender
        
        sqlite_service = container.get('sqlite') if container.has('sqlite') else None
        
        game_recommender = GameRecommender(
            sqlite_service=sqlite_service,
            memory_service=None   # 需要在 API 层初始化
        )
        container.register('game_recommender', game_recommender)
        print("[Container] ✅ 游戏推荐服务已注册（Memory 需要在 API 层初始化）")
    except Exception as e:
        print(f"[Container] ⚠️ 游戏推荐服务注册失败: {e}")
    
    # 业务服务：游戏总结服务（依赖 SQLite + Memory）
    try:
        from services.game import GameSummarizer
        
        sqlite_service = container.get('sqlite') if container.has('sqlite') else None
        
        game_summarizer = GameSummarizer(
            sqlite_service=sqlite_service,
            memory_service=None   # 需要在 API 层初始化
        )
        container.register('game_summarizer', game_summarizer)
        print("[Container] ✅ 游戏总结服务已注册（Memory 需要在 API 层初始化）")
    except Exception as e:
        print(f"[Container] ⚠️ 游戏总结服务注册失败: {e}")
    
    # 业务服务：评估服务（依赖 SQLite + Memory）
    try:
        from services.Assessment import AssessmentService
        
        sqlite_service = container.get('sqlite') if container.has('sqlite') else None
        
        assessment_service = AssessmentService(
            sqlite_service=sqlite_service,
            memory_service=None   # 需要在 API 层初始化
        )
        container.register('assessment', assessment_service)
        print("[Container] ✅ 评估服务已注册（Memory 需要在 API 层初始化）")
    except Exception as e:
        print(f"[Container] ⚠️ 评估服务注册失败: {e}")

    print("[Container] ✅ 核心服务初始化完成")



# ============ 依赖注入函数 ============

async def get_memory_service():
    """获取 Memory 服务（延迟初始化，带 Mock 降级）"""
    try:
        from services.Memory.service import get_memory_service as _get_memory_service
        return await _get_memory_service()
    except Exception as e:
        print(f"[Container] ⚠️ Memory 服务初始化失败 (可能由于 Neo4j 未启动): {e}")
        print("[Container] 🔄 切换到 Mock Memory Service")
        
        class MockMemoryService:
            async def initialize(self): pass
            
            async def add_observation(self, *args, **kwargs):
                return {"status": "mocked", "id": "mock_obs_id"}
                
            async def get_child(self, *args, **kwargs):
                return {"name": "Mock Child", "basic_info": {"diagnosis": "ASD"}}
                
            async def get_relevant_context(self, *args, **kwargs):
                return "Mock context: Child is happy."

            async def import_profile(self, *args, **kwargs):
                return {"child_id": "test_child_001", "assessment_id": "mock_assess_id"}

            async def get_latest_assessment(self, *args, **kwargs):
                return {}
        
        return MockMemoryService()

 
def get_sqlite_service():
    """获取 SQLite 服务"""
    return container.get('sqlite')


def get_file_upload_service():
    """获取文件上传服务"""
    return container.get('file_upload')


def get_llm_service():
    """获取 LLM 服务"""
    return container.get('llm')


async def get_observation_service():
    """获取行为观察服务"""
    observation_service = container.get('observation')
    
    # 延迟初始化 Memory 服务
    if observation_service.memory is None:
        observation_service.memory = await get_memory_service()
    
    return observation_service


async def get_game_recommender():
    """获取游戏推荐服务"""
    game_recommender = container.get('game_recommender')
    
    # 延迟初始化 Memory 服务
    if game_recommender.memory_service is None:
        game_recommender.memory_service = await get_memory_service()
    
    return game_recommender


async def get_game_summarizer():
    """获取游戏总结服务"""
    game_summarizer = container.get('game_summarizer')
    
    # 延迟初始化 Memory 服务
    if game_summarizer.memory_service is None:
        game_summarizer.memory_service = await get_memory_service()
    
    return game_summarizer


def get_game_library():
    """获取游戏库服务"""
    return container.get('game_library')


async def get_assessment_service():
    """获取评估服务"""
    assessment_service = container.get('assessment')
    
    # 延迟初始化 Memory 服务
    if assessment_service.memory_service is None:
        assessment_service.memory_service = await get_memory_service()
    
    return assessment_service
