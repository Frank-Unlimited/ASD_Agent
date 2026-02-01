"""
行为观察服务
提供日常行为记录功能
"""
from typing import Optional, Dict, Any, List
from datetime import datetime


class ObservationService:
    """
    行为观察服务
    
    职责：
    1. 接收家长的行为记录（文字/语音/快速按钮）
    2. 调用 Memory 服务保存记录
    3. 提供行为查询功能
    """
    
    def __init__(self, memory_service, speech_service: Optional[Any] = None):
        """
        初始化行为观察服务
        
        Args:
            memory_service: Memory 服务
            speech_service: 语音服务（可选，用于语音转文字）
        """
        self.memory = memory_service
        self.speech = speech_service
    
    async def record_text_observation(
        self,
        child_id: str,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        记录文字观察
        
        Args:
            child_id: 孩子ID
            text: 观察文字
            context: 可选上下文（如地点、活动等）
        
        Returns:
            行为记录结果
        """
        print(f"[ObservationService] 记录文字观察: child_id={child_id}")
        
        result = await self.memory.record_behavior(
            child_id=child_id,
            raw_input=text,
            input_type="text",
            context=context
        )
        
        print(f"[ObservationService] 记录成功: {result['behavior_id']}")
        
        return {
            "success": True,
            "behavior_id": result['behavior_id'],
            "description": result['description'],
            "event_type": result['event_type'],
            "significance": result['significance'],
            "timestamp": result['timestamp'],
            "message": "行为记录成功"
        }
    
    async def record_voice_observation(
        self,
        child_id: str,
        audio_file: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        记录语音观察
        
        流程：
        1. 调用语音服务转文字
        2. 调用 Memory 服务记录行为
        
        Args:
            child_id: 孩子ID
            audio_file: 音频文件路径
            context: 可选上下文
        
        Returns:
            行为记录结果
        """
        print(f"[ObservationService] 记录语音观察: child_id={child_id}")
        
        if not self.speech:
            raise ValueError("语音服务未配置，无法处理语音记录")
        
        # 1. 语音转文字
        print(f"[ObservationService] 语音转文字中...")
        transcription = await self.speech.transcribe(audio_file)
        text = transcription.get("text", "")
        
        if not text:
            raise ValueError("语音转文字失败，无法识别内容")
        
        print(f"[ObservationService] 识别文字: {text[:50]}...")
        
        # 2. 记录行为
        result = await self.memory.record_behavior(
            child_id=child_id,
            raw_input=text,
            input_type="voice",
            context=context
        )
        
        print(f"[ObservationService] 记录成功: {result['behavior_id']}")
        
        return {
            "success": True,
            "behavior_id": result['behavior_id'],
            "transcription": text,
            "description": result['description'],
            "event_type": result['event_type'],
            "significance": result['significance'],
            "timestamp": result['timestamp'],
            "message": "语音记录成功"
        }
    
    async def record_quick_button(
        self,
        child_id: str,
        button_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        快速按钮记录
        
        预设的快速记录按钮，如：
        - "主动眼神接触"
        - "主动分享玩具"
        - "情绪波动"
        - "拒绝互动"
        
        Args:
            child_id: 孩子ID
            button_type: 按钮类型
            context: 可选上下文
        
        Returns:
            行为记录结果
        """
        print(f"[ObservationService] 快速按钮记录: {button_type}")
        
        # 快速按钮映射
        quick_buttons = {
            "eye_contact": "孩子主动进行眼神接触",
            "share_toy": "孩子主动分享玩具",
            "emotional_outburst": "孩子出现情绪波动",
            "refuse_interaction": "孩子拒绝互动",
            "first_time": "孩子首次出现新行为",
            "breakthrough": "孩子出现突破性进步"
        }
        
        text = quick_buttons.get(button_type, f"快速记录：{button_type}")
        
        # 添加时间戳到上下文
        if context is None:
            context = {}
        context["quick_button"] = button_type
        context["recorded_at"] = datetime.now().isoformat()
        
        result = await self.memory.record_behavior(
            child_id=child_id,
            raw_input=text,
            input_type="quick_button",
            context=context
        )
        
        print(f"[ObservationService] 记录成功: {result['behavior_id']}")
        
        return {
            "success": True,
            "behavior_id": result['behavior_id'],
            "button_type": button_type,
            "description": result['description'],
            "event_type": result['event_type'],
            "significance": result['significance'],
            "timestamp": result['timestamp'],
            "message": "快速记录成功"
        }
    
    async def get_recent_observations(
        self,
        child_id: str,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        获取最近的观察记录
        
        Args:
            child_id: 孩子ID
            limit: 返回数量限制
            filters: 过滤条件（可选）
                - start_time: 开始时间
                - end_time: 结束时间
                - event_type: 事件类型
                - significance: 重要性
        
        Returns:
            观察记录列表
        """
        print(f"[ObservationService] 获取最近观察: child_id={child_id}, limit={limit}")
        
        if filters is None:
            filters = {}
        filters["limit"] = limit
        
        behaviors = await self.memory.get_behaviors(child_id, filters)
        
        print(f"[ObservationService] 找到 {len(behaviors)} 条记录")
        
        return behaviors
    
    async def get_observation_stats(
        self,
        child_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取观察统计
        
        Args:
            child_id: 孩子ID
            days: 统计天数
        
        Returns:
            统计数据
        """
        from datetime import timedelta
        
        print(f"[ObservationService] 获取观察统计: 最近 {days} 天")
        
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # 获取行为记录
        behaviors = await self.memory.get_behaviors(
            child_id,
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "limit": 1000
            }
        )
        
        # 统计
        total_count = len(behaviors)
        
        # 按事件类型统计
        event_types = {}
        for b in behaviors:
            event_type = b.get('event_type', 'other')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # 按重要性统计
        significance_counts = {}
        for b in behaviors:
            sig = b.get('significance', 'normal')
            significance_counts[sig] = significance_counts.get(sig, 0) + 1
        
        # 突破性进步
        breakthroughs = [b for b in behaviors if b.get('significance') == 'breakthrough']
        
        stats = {
            "total_count": total_count,
            "days": days,
            "event_types": event_types,
            "significance_counts": significance_counts,
            "breakthrough_count": len(breakthroughs),
            "recent_breakthroughs": [
                {
                    "description": b.get('description'),
                    "timestamp": b.get('timestamp')
                }
                for b in breakthroughs[:5]
            ]
        }
        
        print(f"[ObservationService] 统计完成: {total_count} 条记录")
        
        return stats


__all__ = ['ObservationService']
