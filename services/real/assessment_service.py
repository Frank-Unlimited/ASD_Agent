"""
真实的初始评估服务 - 使用 LLM
"""
from typing import Dict, Any
from src.interfaces.business import IAssessmentService
from services.real.llm_service import get_llm_service


class RealAssessmentService(IAssessmentService):
    """使用 LLM 的真实评估服务"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    def get_service_name(self) -> str:
        return "RealAssessmentService"
    
    def get_service_version(self) -> str:
        return "1.0.0"
    
    async def build_portrait(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建孩子画像
        
        Args:
            parsed_data: 解析后的医院报告和量表数据
            
        Returns:
            孩子画像字典
        """
        print(f"[Real Assessment] 使用 LLM 构建画像")
        
        # 构建提示词
        system_prompt = """
        你是一位经验丰富的 ASD 儿童评估专家。
        请根据提供的医院报告和量表数据，构建孩子的全面画像。
        
        画像应包括：
        1. strengths: 孩子的优势（数组）
        2. weaknesses: 孩子的弱项（数组）
        3. interests: 孩子的兴趣（数组）
        4. emotionalMilestones: 情感发展里程碑（对象，包含6个维度，每个维度1-6分）
           - selfRegulation: 自我调节
           - intimacy: 亲密关系
           - twoWayCommunication: 双向沟通
           - complexCommunication: 复杂沟通
           - emotionalIdeas: 情感想法
           - logicalThinking: 逻辑思维
        5. customDimensions: 自定义维度（对象）
           - sensorySensitivity: 感觉敏感性 {level: "high/medium/low", triggers: []}
           - repetitiveBehaviors: 重复行为 {frequency: "high/moderate/low"}
        """
        
        user_message = f"""
        孩子信息：
        
        基本信息：
        - 姓名：{parsed_data.get('name', '未知')}
        - 年龄：{parsed_data.get('age', '未知')}
        - 性别：{parsed_data.get('gender', '未知')}
        
        诊断信息：
        - 诊断：{parsed_data.get('diagnosis', '未知')}
        - 严重程度：{parsed_data.get('severity', '未知')}
        
        医院报告摘要：
        {parsed_data.get('report_summary', '无')}
        
        量表结果：
        {parsed_data.get('scale_results', '无')}
        
        请生成完整的孩子画像 JSON。
        """
        
        try:
            portrait = await self.llm.generate_json(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3,
                max_tokens=1500
            )
            
            # 确保必要字段存在
            if "parse_error" not in portrait:
                return portrait
            else:
                # JSON 解析失败，返回默认值
                print(f"[Real Assessment] LLM 返回格式有误，使用默认画像")
                return self._get_default_portrait(parsed_data)
                
        except Exception as e:
            print(f"[Real Assessment] LLM 调用失败: {e}，使用默认画像")
            return self._get_default_portrait(parsed_data)
    
    async def create_observation_framework(self, portrait: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建观察框架
        
        Args:
            portrait: 孩子画像
            
        Returns:
            观察框架字典
        """
        print(f"[Real Assessment] 使用 LLM 创建观察框架")
        
        system_prompt = """
        你是一位 ASD 儿童观察专家。
        根据孩子的画像，创建一个针对性的观察框架。
        
        观察框架应包括：
        1. focusAreas: 重点观察领域（数组，3-5个）
        2. observationPoints: 具体观察要点（数组，5-8个具体描述）
        
        观察要点应该：
        - 具体可操作
        - 与孩子的弱项和发展目标相关
        - 便于家长在日常互动中观察
        """
        
        user_message = f"""
        孩子画像：
        
        优势：{portrait.get('strengths', [])}
        弱项：{portrait.get('weaknesses', [])}
        兴趣：{portrait.get('interests', [])}
        情感发展里程碑：{portrait.get('emotionalMilestones', {})}
        
        请生成观察框架 JSON。
        """
        
        try:
            framework = await self.llm.generate_json(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3,
                max_tokens=1000
            )
            
            if "parse_error" not in framework:
                return framework
            else:
                return self._get_default_framework(portrait)
                
        except Exception as e:
            print(f"[Real Assessment] LLM 调用失败: {e}，使用默认框架")
            return self._get_default_framework(portrait)
    
    def _get_default_portrait(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取默认画像（当 LLM 失败时）"""
        return {
            "strengths": ["待评估"],
            "weaknesses": ["待评估"],
            "interests": parsed_data.get('interests', ["待观察"]),
            "emotionalMilestones": {
                "selfRegulation": 3,
                "intimacy": 3,
                "twoWayCommunication": 3,
                "complexCommunication": 3,
                "emotionalIdeas": 3,
                "logicalThinking": 3
            },
            "customDimensions": {
                "sensorySensitivity": {"level": "medium", "triggers": []},
                "repetitiveBehaviors": {"frequency": "moderate"}
            }
        }
    
    def _get_default_framework(self, portrait: Dict[str, Any]) -> Dict[str, Any]:
        """获取默认观察框架（当 LLM 失败时）"""
        return {
            "focusAreas": ["eyeContact", "twoWayCommunication", "emotionalRegulation"],
            "observationPoints": [
                "眼神接触的频率和时长",
                "主动发起互动的次数",
                "对家长引导的回应性",
                "情绪调节能力",
                "注意力持续时间"
            ]
        }


__all__ = ['RealAssessmentService']
