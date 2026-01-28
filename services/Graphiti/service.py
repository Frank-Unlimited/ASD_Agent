"""
Graphiti 核心服务实现
封装 graphiti-core 的底层功能
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

from graphiti_core import Graphiti
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

try:
    from .config import GraphitiConfig
except ImportError:
    from config import GraphitiConfig

# 从项目配置读取 LLM 设置
from src.config import settings


class GraphitiService:
    """Graphiti 核心服务"""
    
    def __init__(self, config: Optional[GraphitiConfig] = None):
        """
        初始化 Graphiti 服务
        
        Args:
            config: Graphiti 配置，如果为 None 则使用默认配置
        """
        self.config = config or GraphitiConfig(
            neo4j_uri=settings.neo4j_uri,
            neo4j_user=settings.neo4j_user,
            neo4j_password=settings.neo4j_password
        )
        
        # 创建 LLM 客户端和 Embedder（使用统一配置）
        llm_client, embedder = self._create_llm_client()
        
        # 为 Graphiti 设置环境变量（用于 reranker）
        import os
        if settings.llm_api_key:
            os.environ['OPENAI_API_KEY'] = settings.llm_api_key
        
        # 初始化 Graphiti 客户端
        self.client = Graphiti(
            uri=self.config.neo4j_uri,
            user=self.config.neo4j_user,
            password=self.config.neo4j_password,
            llm_client=llm_client,
            embedder=embedder
        )
        
        print(f"[Graphiti Service] 已连接到 Neo4j: {self.config.neo4j_uri}")
        print(f"[Graphiti Service] 使用 LLM: {settings.llm_model}")
    
    def _create_llm_client(self):
        """根据统一配置创建 LLM 客户端和 Embedder"""
        api_key = settings.llm_api_key
        if not api_key:
            raise ValueError("LLM_API_KEY is required")
        
        llm_config = LLMConfig(
            api_key=api_key,
            model=settings.llm_model,
            small_model=settings.llm_small_model,
            base_url=settings.llm_base_url
        )
        
        llm_client = OpenAIGenericClient(config=llm_config)
        
        embedder_config = OpenAIEmbedderConfig(
            api_key=api_key,
            embedding_model=settings.llm_embedding_model,
            embedding_dim=settings.llm_embedding_dim,
            base_url=settings.llm_base_url
        )
        
        embedder = OpenAIEmbedder(config=embedder_config)
        
        return llm_client, embedder
    
    # ============ 核心功能方法 ============
    
    async def add_episode(
        self,
        child_id: str,
        episode_name: str,
        episode_content: str,
        reference_time: datetime
    ) -> None:
        """
        添加一个 episode（记忆片段）到 Graphiti
        
        Args:
            child_id: 孩子ID
            episode_name: Episode 名称
            episode_content: Episode 内容
            reference_time: 参考时间
        """
        await self.client.add_episode(
            name=episode_name,
            episode_body=episode_content,
            source_description=f"ASD干预系统 - 孩子 {child_id}",
            reference_time=reference_time
        )
    
    async def search_memories(
        self,
        query: str,
        num_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            记忆列表
        """
        search_results = await self.client.search(
            query=query,
            num_results=num_results
        )
        
        # 转换为标准格式
        memories = []
        
        # search_results 可能是列表或对象
        if isinstance(search_results, list):
            # 直接是列表
            for edge in search_results:
                memories.append({
                    "fact": edge.fact if hasattr(edge, 'fact') else str(edge),
                    "source_node": edge.source_node_uuid if hasattr(edge, 'source_node_uuid') else None,
                    "target_node": edge.target_node_uuid if hasattr(edge, 'target_node_uuid') else None,
                    "created_at": edge.created_at.isoformat() if hasattr(edge, 'created_at') and edge.created_at else None,
                    "valid_at": edge.valid_at.isoformat() if hasattr(edge, 'valid_at') and edge.valid_at else None,
                    "invalid_at": edge.invalid_at.isoformat() if hasattr(edge, 'invalid_at') and edge.invalid_at else None,
                })
        else:
            # 是对象，有 edges 属性
            for edge in search_results.edges:
                memories.append({
                    "fact": edge.fact,
                    "source_node": edge.source_node_uuid,
                    "target_node": edge.target_node_uuid,
                    "created_at": edge.created_at.isoformat() if edge.created_at else None,
                    "valid_at": edge.valid_at.isoformat() if edge.valid_at else None,
                    "invalid_at": edge.invalid_at.isoformat() if edge.invalid_at else None,
                })
        
        return memories
    
    async def close(self):
        """关闭连接"""
        try:
            await self.client.close()
            print("[Graphiti Service] 连接已关闭")
        except Exception as e:
            print(f"[Graphiti Service] 关闭连接失败: {str(e)}")


# 全局服务实例（单例模式）
_service_instance: Optional[GraphitiService] = None


def get_service(config: Optional[GraphitiConfig] = None) -> GraphitiService:
    """获取 Graphiti 服务实例（单例）"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = GraphitiService(config)
    
    return _service_instance
