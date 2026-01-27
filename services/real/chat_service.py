"""
真实的对话助手服务 - 使用 LLM
"""
from typing import Dict, Any, List
from src.interfaces.business import IChatAssistantService
from services.real.llm_service import get_llm_service


class RealChatAssistantService(IChatAssistantService):
    """使用 LLM 的真实对话助手"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    def get_service_name(self) -> str:
        return "RealChatAssistantService"
    
    def get_service_version(self) -> str:
        return "1.0.0"
    
    async def chat(
        self, 
        child_id: str, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        对话接口
        
        Args:
            child_id: 孩子ID
            user_message: 用户消息
            conversation_history: 对话历史
            
        Returns:
            包含回复和来源的字典
        """
        print(f"[Real Chat] 处理用户消息: {user_message[:50]}...")
        
        # 构建系统提示词
        system_prompt = """
        你是一位专业、温暖的 ASD 儿童干预助手。你的职责是：
        
        1. 回答家长关于 ASD 干预、地板时光疗法的问题
        2. 提供实用的育儿建议和游戏指导
        3. 解读孩子的行为表现
        4. 给予情感支持和鼓励
        
        回答要求：
        - 专业但易懂，避免过多术语
        - 温暖有同理心
        - 具体可操作
        - 如果涉及医疗诊断，提醒家长咨询专业医生
        """
        
        try:
            # 转换对话历史格式
            history = []
            for msg in conversation_history[-10:]:  # 只保留最近10轮对话
                if msg.get('role') in ['user', 'assistant']:
                    history.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            # 调用 LLM
            response = await self.llm.chat_with_history(
                system_prompt=system_prompt,
                conversation_history=history,
                user_message=user_message,
                temperature=0.7,
                max_tokens=800
            )
            
            return {
                "response": response,
                "sources": [],  # TODO: 后续可以添加 RAG 检索的来源
                "confidence": 0.9
            }
            
        except Exception as e:
            print(f"[Real Chat] LLM 调用失败: {e}")
            return {
                "response": "抱歉，我现在遇到了一些技术问题。请稍后再试，或者联系我们的支持团队。",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def route_query(self, query: str) -> str:
        """
        路由查询到不同的处理模块
        
        Args:
            query: 用户查询
            
        Returns:
            路由类型 (general, game_recommendation, behavior_analysis, etc.)
        """
        print(f"[Real Chat] 路由查询: {query[:50]}...")
        
        system_prompt = """
        你是一个查询路由器。根据用户的问题，判断应该路由到哪个模块。
        
        可选的路由类型：
        - general: 一般性问题、闲聊
        - game_recommendation: 游戏推荐、活动建议
        - behavior_analysis: 行为分析、表现解读
        - progress_inquiry: 进展查询、数据查看
        - guidance: 实时指导、话术建议
        - knowledge: 知识查询（ASD、地板时光等）
        
        只返回路由类型，不要其他内容。
        """
        
        user_message = f"用户问题：{query}\n\n请返回路由类型。"
        
        try:
            route = await self.llm.chat_with_system(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.1,
                max_tokens=50
            )
            
            # 清理返回值
            route = route.strip().lower()
            
            # 验证路由类型
            valid_routes = [
                'general', 'game_recommendation', 'behavior_analysis',
                'progress_inquiry', 'guidance', 'knowledge'
            ]
            
            if route in valid_routes:
                return route
            else:
                return 'general'
                
        except Exception as e:
            print(f"[Real Chat] 路由失败: {e}，使用默认路由")
            return 'general'


__all__ = ['RealChatAssistantService']
