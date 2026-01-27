"""
Graphiti 记忆网络真实实现
基于 graphiti-core 库
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import os
from src.interfaces import IGraphitiService
from graphiti_core import Graphiti
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from src.config import settings


class GraphitiService(IGraphitiService):
    """Graphiti 真实服务实现"""
    
    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str
    ):
        """
        初始化 Graphiti 服务
        
        Args:
            neo4j_uri: Neo4j 数据库 URI (如 bolt://localhost:7688)
            neo4j_user: Neo4j 用户名
            neo4j_password: Neo4j 密码
        
        Note:
            LLM 配置从 settings 中读取，支持 DeepSeek/OpenAI/Gemini
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # 根据配置选择 LLM 提供商
        llm_client, embedder = self._create_llm_client()
        
        # 初始化 Graphiti 客户端
        self.client = Graphiti(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
            llm_client=llm_client,
            embedder=embedder
        )
        
        print(f"[Graphiti Service] 已连接到 Neo4j: {neo4j_uri}")
        print(f"[Graphiti Service] 使用 LLM: {settings.ai_provider}")
    
    def _create_llm_client(self):
        """
        根据配置创建 LLM 客户端和 Embedder
        保持与项目 LLM 服务配置一致
        """
        if settings.ai_provider == "deepseek":
            # DeepSeek 配置
            api_key = settings.deepseek_api_key
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY is required when using DeepSeek")
            
            llm_config = LLMConfig(
                api_key=api_key,
                model=settings.deepseek_model,
                small_model=settings.deepseek_small_model,
                base_url=f"{settings.deepseek_base_url}/v1"
            )
            
            llm_client = OpenAIGenericClient(config=llm_config)
            
            # DeepSeek 的 embedding
            embedder_config = OpenAIEmbedderConfig(
                api_key=api_key,
                embedding_model=settings.deepseek_embedding_model,
                embedding_dim=settings.deepseek_embedding_dim,
                base_url=f"{settings.deepseek_base_url}/v1"
            )
            
            embedder = OpenAIEmbedder(config=embedder_config)
            
        elif settings.ai_provider == "openai":
            # OpenAI 配置
            api_key = settings.openai_api_key
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI")
            
            llm_config = LLMConfig(
                api_key=api_key,
                model=settings.openai_model,
                small_model=settings.openai_small_model
            )
            
            llm_client = OpenAIGenericClient(config=llm_config)
            
            embedder_config = OpenAIEmbedderConfig(
                api_key=api_key,
                embedding_model=settings.openai_embedding_model,
                embedding_dim=settings.openai_embedding_dim
            )
            
            embedder = OpenAIEmbedder(config=embedder_config)
            
        elif settings.ai_provider == "gemini":
            # Gemini 配置
            from graphiti_core.llm_client.gemini_client import GeminiClient
            from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
            
            api_key = settings.gemini_api_key
            if not api_key:
                raise ValueError("GEMINI_API_KEY is required when using Gemini")
            
            llm_config = LLMConfig(
                api_key=api_key,
                model=settings.gemini_model
            )
            
            llm_client = GeminiClient(config=llm_config)
            
            embedder_config = GeminiEmbedderConfig(
                api_key=api_key,
                embedding_model=settings.gemini_embedding_model
            )
            
            embedder = GeminiEmbedder(config=embedder_config)
            
        else:
            raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
        
        return llm_client, embedder
    
    def get_service_name(self) -> str:
        return "GraphitiService"
    
    def get_service_version(self) -> str:
        return "1.0.0"
    
    async def save_memories(self, child_id: str, memories: List[Dict[str, Any]]) -> None:
        """
        批量保存记忆到 Graphiti
        
        Args:
            child_id: 孩子ID
            memories: 记忆列表，每个记忆包含:
                - timestamp: 时间戳
                - type: 类型 (observation/milestone/feedback)
                - content: 内容描述
                - metadata: 元数据
        """
        print(f"[Graphiti Service] 批量保存记忆: {child_id}, count={len(memories)}")
        
        try:
            # 为每个记忆创建 episode
            for memory in memories:
                episode_content = self._format_memory_content(memory)
                
                # 添加到 Graphiti（新版本 API）
                await self.client.add_episode(
                    name=f"{child_id}_{memory.get('type', 'observation')}_{memory.get('timestamp')}",
                    episode_body=episode_content,
                    source_description=f"ASD干预系统 - 孩子 {child_id}",
                    reference_time=datetime.fromisoformat(memory.get('timestamp', datetime.now().isoformat()))
                )
            
            print(f"[Graphiti Service] 成功保存 {len(memories)} 条记忆")
            
        except Exception as e:
            print(f"[Graphiti Service] 保存记忆失败: {str(e)}")
            raise
    
    async def get_recent_memories(self, child_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取最近的记忆
        
        Args:
            child_id: 孩子ID
            days: 最近多少天
            
        Returns:
            记忆列表
        """
        print(f"[Graphiti Service] 获取最近记忆: {child_id}, days={days}")
        
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 搜索相关记忆
            search_results = await self.client.search(
                query=f"孩子 {child_id} 的观察记录和进展",
                num_results=50
            )
            
            # 转换为标准格式
            memories = []
            for result in search_results.edges:
                memories.append({
                    "timestamp": result.created_at.isoformat() if result.created_at else None,
                    "type": "observation",
                    "content": result.fact,
                    "source": result.source_node_uuid,
                    "target": result.target_node_uuid,
                    "confidence": 0.8
                })
            
            print(f"[Graphiti Service] 找到 {len(memories)} 条记忆")
            return memories
            
        except Exception as e:
            print(f"[Graphiti Service] 获取记忆失败: {str(e)}")
            return []
    
    async def analyze_trends(self, child_id: str, dimension: str) -> Dict[str, Any]:
        """
        分析某个维度的趋势
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称 (如 eye_contact, two_way_communication)
            
        Returns:
            趋势分析结果
        """
        print(f"[Graphiti Service] 分析趋势: {child_id}, dimension={dimension}")
        
        try:
            # 搜索该维度相关的记忆
            search_results = await self.client.search(
                query=f"孩子 {child_id} 在 {dimension} 维度的表现和变化",
                num_results=30
            )
            
            # 简单的趋势分析（实际应该更复杂）
            if len(search_results.edges) > 0:
                # 这里简化处理，实际应该分析时序数据
                trend = "improving" if len(search_results.edges) > 10 else "stable"
                rate = len(search_results.edges) / 30.0
            else:
                trend = "unknown"
                rate = 0.0
            
            return {
                "dimension": dimension,
                "trend": trend,
                "rate": rate,
                "dataPoints": len(search_results.edges),
                "lastUpdated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[Graphiti Service] 趋势分析失败: {str(e)}")
            return {
                "dimension": dimension,
                "trend": "unknown",
                "rate": 0.0,
                "dataPoints": 0
            }
    
    async def detect_milestones(self, child_id: str) -> List[Dict[str, Any]]:
        """
        检测里程碑事件
        
        Args:
            child_id: 孩子ID
            
        Returns:
            里程碑列表
        """
        print(f"[Graphiti Service] 检测里程碑: {child_id}")
        
        try:
            # 搜索里程碑相关的记忆
            search_results = await self.client.search(
                query=f"孩子 {child_id} 的重要突破、首次出现、显著进步",
                num_results=20
            )
            
            # 转换为里程碑格式
            milestones = []
            for result in search_results.edges:
                if "首次" in result.fact or "突破" in result.fact or "进步" in result.fact:
                    milestones.append({
                        "timestamp": result.created_at.isoformat() if result.created_at else None,
                        "type": "breakthrough",
                        "description": result.fact,
                        "dimension": "unknown",  # 需要从内容中提取
                        "significance": "high"
                    })
            
            print(f"[Graphiti Service] 检测到 {len(milestones)} 个里程碑")
            return milestones
            
        except Exception as e:
            print(f"[Graphiti Service] 里程碑检测失败: {str(e)}")
            return []
    
    async def detect_plateau(self, child_id: str, dimension: str) -> Dict[str, Any]:
        """
        检测平台期
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            
        Returns:
            平台期检测结果
        """
        print(f"[Graphiti Service] 检测平台期: {child_id}, dimension={dimension}")
        
        try:
            # 获取最近的趋势
            trend_result = await self.analyze_trends(child_id, dimension)
            
            # 简单判断：如果趋势是 stable 且数据点较多，可能是平台期
            is_plateau = (
                trend_result["trend"] == "stable" and 
                trend_result["dataPoints"] > 15
            )
            
            return {
                "dimension": dimension,
                "isPlateau": is_plateau,
                "duration": 3 if is_plateau else 0,  # 简化处理
                "suggestion": "考虑调整干预策略" if is_plateau else "继续当前计划"
            }
            
        except Exception as e:
            print(f"[Graphiti Service] 平台期检测失败: {str(e)}")
            return {
                "dimension": dimension,
                "isPlateau": False,
                "duration": 0,
                "suggestion": "数据不足"
            }
    
    async def build_context(self, child_id: str) -> Dict[str, Any]:
        """
        构建当前上下文
        
        Args:
            child_id: 孩子ID
            
        Returns:
            上下文数据（包含趋势、关注点、活跃目标等）
        """
        print(f"[Graphiti Service] 构建上下文: {child_id}")
        
        try:
            # 并行获取多个维度的数据
            dimensions = [
                "eye_contact",
                "two_way_communication",
                "emotional_regulation"
            ]
            
            # 获取趋势
            trend_tasks = [
                self.analyze_trends(child_id, dim) 
                for dim in dimensions
            ]
            trends = await asyncio.gather(*trend_tasks)
            
            # 获取里程碑
            milestones = await self.detect_milestones(child_id)
            
            # 获取最近记忆
            recent_memories = await self.get_recent_memories(child_id, days=7)
            
            # 构建上下文
            context = {
                "recentTrends": {
                    dim: trend 
                    for dim, trend in zip(dimensions, trends)
                },
                "attentionPoints": self._extract_attention_points(trends),
                "activeGoals": self._extract_active_goals(recent_memories),
                "recentMilestones": milestones[:3],  # 最近3个里程碑
                "lastUpdated": datetime.now().isoformat()
            }
            
            print(f"[Graphiti Service] 上下文构建完成")
            return context
            
        except Exception as e:
            print(f"[Graphiti Service] 构建上下文失败: {str(e)}")
            return {
                "recentTrends": {},
                "attentionPoints": [],
                "activeGoals": [],
                "recentMilestones": [],
                "lastUpdated": datetime.now().isoformat()
            }
    
    # ============ 辅助方法 ============
    
    def _format_memory_content(self, memory: Dict[str, Any]) -> str:
        """格式化记忆内容为文本"""
        content = memory.get('content', '')
        memory_type = memory.get('type', 'observation')
        timestamp = memory.get('timestamp', '')
        
        return f"""
时间: {timestamp}
类型: {memory_type}
内容: {content}
元数据: {memory.get('metadata', {})}
"""
    
    def _extract_attention_points(self, trends: List[Dict[str, Any]]) -> List[str]:
        """从趋势中提取关注点"""
        attention_points = []
        
        for trend in trends:
            if trend.get("trend") == "declining":
                attention_points.append(f"{trend['dimension']} 需要关注")
            elif trend.get("trend") == "improving":
                attention_points.append(f"{trend['dimension']} 进展良好")
        
        return attention_points
    
    def _extract_active_goals(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从记忆中提取活跃目标"""
        # 简化处理，实际应该从记忆中智能提取
        return [
            {
                "goal": "提升眼神接触频率",
                "status": "in_progress",
                "progress": 0.6
            }
        ]
    
    async def close(self):
        """关闭连接"""
        try:
            await self.client.close()
            print("[Graphiti Service] 连接已关闭")
        except Exception as e:
            print(f"[Graphiti Service] 关闭连接失败: {str(e)}")
