"""
测试从图片导入档案（需要准备医学报告图片）
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.container import get_memory_service, get_sqlite_service
from services.Multimodal_Understanding.api_interface import parse_image
from services.Multimodal_Understanding.utils import encode_local_image


async def test_image_import():
    """测试图片导入档案"""
    print("\n" + "="*60)
    print("测试图片导入档案")
    print("="*60)
    
    # 1. 检查测试图片
    test_image_path = "test_medical_report.jpg"  # 需要准备一张医学报告图片
    
    if not os.path.exists(test_image_path):
        print(f"\n❌ 测试图片不存在: {test_image_path}")
        print("请准备一张医学报告图片，命名为 test_medical_report.jpg")
        return
    
    print(f"\n[1] 找到测试图片: {test_image_path}")
    
    # 2. 初始化服务
    print("\n[2] 初始化服务...")
    memory_service = await get_memory_service()
    sqlite_service = get_sqlite_service()
    print("✅ 服务初始化成功")
    
    # 3. 提取文字并生成画像
    print("\n[3] 提取文字并生成画像...")
    
    image_base64 = encode_local_image(test_image_path)
    
    prompt = """
请完成两个任务：

1. 提取这张医学报告中的所有文字内容，保持原有格式和结构。

2. 基于提取的内容，生成一个简短的孩子画像总结（100-150字），包括：
   - 孩子的基本情况（年龄、诊断）
   - 主要特点和表现
   - 当前的发展状况
   - 需要关注的重点

请按以下格式输出：

【提取的文字】
（这里是完整的文字内容）

【孩子画像】
（这里是100-150字的画像总结）
"""
    
    result_text = parse_image(image_base64, prompt)
    
    print(f"\n✅ 文字提取完成")
    print(f"提取结果（前500字）:\n{result_text[:500]}...")
    
    # 4. 分离提取的文字和画像总结
    extracted_text = ""
    profile_summary = ""
    
    if "【提取的文字】" in result_text and "【孩子画像】" in result_text:
        parts = result_text.split("【孩子画像】")
        extracted_text = parts[0].replace("【提取的文字】", "").strip()
        profile_summary = parts[1].strip()
    else:
        extracted_text = result_text
        profile_summary = "档案已导入，正在生成详细评估..."
    
    print(f"\n提取文字: {extracted_text[:200]}...")
    print(f"\n画像总结: {profile_summary[:100]}...")
    
    # 5. 构建档案数据
    profile_data = {
        "name": "待解析",
        "age": 0,
        "diagnosis": "",
        "medical_reports": extracted_text,
        "assessment_scales": "",
        "image_path": test_image_path
    }
    
    # 6. 调用 Memory 服务导入
    print("\n[4] 调用 Memory 服务导入...")
    result = await memory_service.import_profile(profile_data)
    
    print(f"\n✅ 档案导入成功")
    print(f"   - 孩子ID: {result['child_id']}")
    print(f"   - 评估ID: {result['assessment_id']}")
    print(f"   - 消息: {result['message']}")
    print(f"   - 画像总结: {profile_summary}")
    
    # 7. 验证档案
    print("\n[5] 验证档案...")
    child = sqlite_service.get_child(result['child_id'])
    if child:
        print(f"✅ 档案已保存到 SQLite")
        print(f"   - 姓名: {child.name}")
        print(f"   - 基本信息: {child.basic_info}")
    
    # 8. 验证评估
    print("\n[6] 验证评估...")
    assessment = await memory_service.get_latest_assessment(
        result['child_id'],
        "comprehensive"
    )
    if assessment:
        print(f"✅ 初始评估已生成")
        print(f"   - 评估ID: {assessment['assessment_id']}")
        print(f"   - 分析结果: {str(assessment.get('analysis', {}))[:200]}...")
    
    # 9. 关闭服务
    print("\n[7] 关闭服务...")
    await memory_service.close()
    print("✅ 服务已关闭")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_image_import())
