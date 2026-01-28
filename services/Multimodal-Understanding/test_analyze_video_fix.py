"""
测试 analyze_video 修复
验证是否能正确解析 AI 返回的文本
"""
import asyncio
import json
import sys
import importlib
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 动态导入带连字符的模块
multimodal_adapters = importlib.import_module('services.Multimodal-Understanding.adapters')
MultimodalVideoAnalysisService = multimodal_adapters.MultimodalVideoAnalysisService


def test_parse_json_response():
    """测试JSON解析功能"""
    
    service = MultimodalVideoAnalysisService()
    
    # 测试1: 标准JSON格式
    json_text = """
    ```json
    {
        "behaviors": [
            {
                "description": "孩子主动与妈妈进行眼神接触",
                "timestamp": "00:15",
                "significance": 4,
                "type": "eye_contact"
            }
        ],
        "interactions": [
            {
                "description": "对妈妈的呼唤有回应",
                "timestamp": "00:30",
                "quality": 4,
                "type": "response"
            }
        ],
        "emotions": {
            "dominant_emotion": "happy",
            "changes": [],
            "regulation_ability": "良好"
        },
        "attention": {
            "duration": "moderate",
            "quality": "good",
            "focus_shifts": []
        },
        "summary": "孩子整体表现良好，眼神接触频率较高",
        "highlights": [
            {
                "timestamp": "00:15",
                "description": "主动眼神接触",
                "importance": "high"
            }
        ]
    }
    ```
    """
    
    try:
        result = service._parse_analysis_text(json_text)
        print("✓ 测试1通过: 标准JSON格式解析成功")
        print(f"  - behaviors: {len(result['behaviors'])} 条")
        print(f"  - interactions: {len(result['interactions'])} 条")
        print(f"  - dominant_emotion: {result['emotions']['dominant_emotion']}")
        assert len(result['behaviors']) == 1
        assert result['behaviors'][0]['description'] == "孩子主动与妈妈进行眼神接触"
    except Exception as e:
        print(f"✗ 测试1失败: {e}")
        return False
    
    # 测试2: 无代码块的JSON
    json_text2 = """
    {
        "behaviors": [{"description": "测试行为", "timestamp": "00:00", "significance": 3, "type": "other"}],
        "interactions": [],
        "emotions": {"dominant_emotion": "calm"},
        "attention": {"duration": "short", "quality": "fair"},
        "summary": "测试总结"
    }
    """
    
    try:
        result = service._parse_analysis_text(json_text2)
        print("✓ 测试2通过: 无代码块JSON解析成功")
        assert len(result['behaviors']) == 1
    except Exception as e:
        print(f"✗ 测试2失败: {e}")
        return False
    
    return True


def test_fallback_parse():
    """测试降级解析功能"""
    
    service = MultimodalVideoAnalysisService()
    
    # 测试纯文本分析
    text = """
    视频分析结果：
    
    孩子在视频中表现出良好的眼神接触能力，多次主动看向妈妈。
    在互动环节，孩子能够回应妈妈的呼唤，表现出较好的互动意愿。
    情绪方面，孩子整体保持开心愉快的状态。
    注意力方面，孩子能够专注于游戏活动，持续时间较长。
    
    总体来说，孩子的表现令人满意。
    """
    
    try:
        result = service._fallback_parse(text)
        print("✓ 测试3通过: 降级解析成功")
        print(f"  - behaviors: {len(result['behaviors'])} 条")
        print(f"  - interactions: {len(result['interactions'])} 条")
        print(f"  - dominant_emotion: {result['emotions']['dominant_emotion']}")
        print(f"  - attention duration: {result['attention']['duration']}")
        
        # 验证提取了关键信息
        assert len(result['behaviors']) > 0
        assert len(result['interactions']) > 0
        assert result['emotions']['dominant_emotion'] == 'happy'  # 因为文本中有"开心"
        assert result['attention']['duration'] == 'long'  # 因为文本中有"持续时间较长"
        
    except Exception as e:
        print(f"✗ 测试3失败: {e}")
        return False
    
    return True


def test_structured_prompt():
    """测试结构化提示词生成"""
    
    service = MultimodalVideoAnalysisService()
    
    context = {
        'child_profile': {
            'name': '小明',
            'age': 36
        }
    }
    
    prompt = service._build_structured_prompt(context)
    
    print("✓ 测试4通过: 结构化提示词生成成功")
    print(f"  - 提示词长度: {len(prompt)} 字符")
    
    # 验证提示词包含关键元素
    assert '小明' in prompt
    assert '36个月' in prompt
    assert 'JSON' in prompt
    assert 'behaviors' in prompt
    assert 'interactions' in prompt
    assert 'emotions' in prompt
    assert 'attention' in prompt
    
    return True


async def test_full_integration():
    """测试完整集成（模拟）"""
    
    service = MultimodalVideoAnalysisService()
    
    # 模拟AI返回的JSON响应
    mock_response = """
    ```json
    {
        "behaviors": [
            {
                "description": "孩子在00:15秒时主动与妈妈进行眼神接触",
                "timestamp": "00:15",
                "significance": 5,
                "type": "eye_contact"
            },
            {
                "description": "在00:45秒时出现拍手动作",
                "timestamp": "00:45",
                "significance": 3,
                "type": "body_movement"
            }
        ],
        "interactions": [
            {
                "description": "对妈妈的呼唤立即回应",
                "timestamp": "00:30",
                "quality": 5,
                "type": "response"
            }
        ],
        "emotions": {
            "dominant_emotion": "happy",
            "changes": [
                {
                    "timestamp": "01:00",
                    "from": "calm",
                    "to": "happy",
                    "trigger": "妈妈给予表扬"
                }
            ],
            "regulation_ability": "良好，能够快速从轻微不适中恢复"
        },
        "attention": {
            "duration": "long",
            "quality": "good",
            "focus_shifts": [
                {
                    "timestamp": "00:50",
                    "from": "玩具",
                    "to": "妈妈"
                }
            ]
        },
        "summary": "孩子整体表现优秀，眼神接触频率高，互动回应及时，情绪稳定愉快，注意力集中。",
        "highlights": [
            {
                "timestamp": "00:15",
                "description": "主动眼神接触，持续3秒",
                "importance": "high"
            },
            {
                "timestamp": "00:30",
                "description": "快速回应妈妈呼唤",
                "importance": "high"
            }
        ]
    }
    ```
    """
    
    # 测试解析
    try:
        result = service._parse_analysis_text(mock_response)
        print("✓ 测试5通过: 完整集成测试成功")
        print(f"  - 解析到 {len(result['behaviors'])} 个行为")
        print(f"  - 解析到 {len(result['interactions'])} 个互动")
        print(f"  - 解析到 {len(result['highlights'])} 个亮点")
        print(f"  - 主要情绪: {result['emotions']['dominant_emotion']}")
        print(f"  - 注意力质量: {result['attention']['quality']}")
        
        # 验证数据完整性
        assert len(result['behaviors']) == 2
        assert len(result['interactions']) == 1
        assert len(result['highlights']) == 2
        assert result['emotions']['dominant_emotion'] == 'happy'
        assert result['attention']['duration'] == 'long'
        
        return True
    except Exception as e:
        print(f"✗ 测试5失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试 Multimodal analyze_video 修复")
    print("=" * 60)
    print()
    
    tests = [
        ("JSON解析测试", test_parse_json_response),
        ("降级解析测试", test_fallback_parse),
        ("提示词生成测试", test_structured_prompt),
        ("完整集成测试", lambda: asyncio.run(test_full_integration())),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {name} 异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
