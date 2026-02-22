"""
动态 Schema 构建器
从 Pydantic Model 自动生成 OpenAI JSON Schema
"""
from typing import Type, Dict, Any
from pydantic import BaseModel


def pydantic_to_json_schema(
    model: Type[BaseModel],
    schema_name: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    从 Pydantic Model 动态生成 OpenAI JSON Schema
    
    优势：
    - 只需修改 src/models 中的数据模型定义
    - Schema 自动同步更新
    - 类型安全，有 IDE 提示
    
    Args:
        model: Pydantic Model 类
        schema_name: Schema 名称
        description: Schema 描述
        
    Returns:
        OpenAI JSON Schema 格式
    """
    # 获取 Pydantic 的 JSON Schema
    pydantic_schema = model.model_json_schema()
    
    # 转换为 OpenAI 要求的格式
    openai_schema = {
        "name": schema_name,
        "description": description or pydantic_schema.get("description", ""),
        "strict": True,
        "schema": {
            "type": "object",
            "properties": pydantic_schema.get("properties", {}),
            "required": pydantic_schema.get("required", []),
            "additionalProperties": False
        }
    }
    
    # 处理嵌套的 $defs（Pydantic 用于存储引用的子模型）
    if "$defs" in pydantic_schema:
        openai_schema["schema"]["$defs"] = pydantic_schema["$defs"]
    
    return openai_schema


__all__ = ['pydantic_to_json_schema']
