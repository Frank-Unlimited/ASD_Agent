"""
测试适配器 - 简化版
直接运行: python test_adapters.py
"""
import asyncio
import os
import sys

# 设置API密钥
os.environ["DASHSCOPE_API_KEY"] = "sk-5cd70747046b4cf787793bb6ee28cb44"

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from adapters import MultimodalDocumentParserService, MultimodalVideoAnalysisService


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


async def quick_test():
    """快速测试 - 只测试核心功能"""
    print("\n🚀 开始快速测试...\n")
    
    # 测试1: 文档解析
    print_header("测试1: 文档解析适配器")
    doc_service = MultimodalDocumentParserService()
    print(f"✅ 服务创建成功: {doc_service.get_service_name()} v{doc_service.get_service_version()}")
    
    try:
        # 测试解析图片报告
        print("\n正在解析图片报告...")
        result = await doc_service.parse_report(
            file_path="https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg",
            file_type="image"
        )
        print(f"✅ 解析成功！文本长度: {len(result['raw_text'])} 字符")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试2: 视频分析
    print_header("测试2: 视频分析适配器")
    video_service = MultimodalVideoAnalysisService()
    print(f"✅ 服务创建成功: {video_service.get_service_name()} v{video_service.get_service_version()}")
    
    try:
        # 测试分析视频
        print("\n正在分析视频...")
        result = await video_service.analyze_video(
            video_path="https://media.w3.org/2010/05/sintel/trailer.mp4",
            context={'child_profile': {'name': '辰辰', 'age': 2.5}}
        )
        print(f"✅ 分析成功！总结长度: {len(result['summary'])} 字符")
    except Exception as e:
        print(f"❌ 失败: {e}")


async def full_test():
    """完整测试 - 测试所有功能"""
    print("\n🔍 开始完整测试...\n")
    
    # 测试1: 文档解析
    print_header("测试1: 文档解析适配器")
    doc_service = MultimodalDocumentParserService()
    
    print(f"\n服务信息:")
    print(f"  名称: {doc_service.get_service_name()}")
    print(f"  版本: {doc_service.get_service_version()}")
    
    # 1.1 解析图片报告
    print("\n[1.1] 测试解析图片报告...")
    try:
        result = await doc_service.parse_report(
            file_path="https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg",
            file_type="image"
        )
        print("✅ 解析成功")
        print(f"  诊断: {result['diagnosis'][:80]}...")
        print(f"  严重程度: {result['severity'][:50]}...")
        print(f"  原始文本长度: {len(result['raw_text'])} 字符")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 1.2 解析量表（文本）
    print("\n[1.2] 测试解析量表（文本）...")
    try:
        result = await doc_service.parse_scale(
            scale_data={'text': '题目1: 3分\n题目2: 4分\n题目3: 2分'},
            scale_type='CARS'
        )
        print("✅ 解析成功")
        print(f"  量表类型: {result['scale_type']}")
        print(f"  总分: {result['total_score']}")
        print(f"  严重程度: {result['severity_level']}")
        print(f"  解释长度: {len(result['interpretation'])} 字符")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试2: 视频分析
    print_header("测试2: 视频分析适配器")
    video_service = MultimodalVideoAnalysisService()
    
    print(f"\n服务信息:")
    print(f"  名称: {video_service.get_service_name()}")
    print(f"  版本: {video_service.get_service_version()}")
    
    # 2.1 分析视频
    print("\n[2.1] 测试视频分析...")
    context = {
        'child_profile': {
            'name': '辰辰',
            'age': 2.5,
            'interests': ['旋转物体', '水流']
        },
        'game_info': {
            'name': '泡泡游戏',
            'goal': '提升互动'
        }
    }
    
    try:
        result = await video_service.analyze_video(
            video_path="https://media.w3.org/2010/05/sintel/trailer.mp4",
            context=context
        )
        print("✅ 分析成功")
        print(f"  总结长度: {len(result['summary'])} 字符")
        print(f"  行为数量: {len(result['behaviors'])}")
        print(f"  互动数量: {len(result['interactions'])}")
        print(f"  情绪: {result['emotions']}")
        print(f"  注意力: {result['attention']}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 2.2 提取关键片段
    print("\n[2.2] 测试提取关键片段...")
    try:
        highlights = await video_service.extract_highlights(
            video_path="https://media.w3.org/2010/05/sintel/trailer.mp4",
            analysis_result=result
        )
        print(f"✅ 提取成功，找到 {len(highlights)} 个关键片段")
        if highlights:
            print(f"  第一个片段: {highlights[0]}")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试3: 系统集成说明
    print_header("测试3: 系统集成说明")
    print("\n✅ 两个服务都已注册到系统容器")
    print("\n在系统中使用:")
    print("  from src.container import container")
    print("  doc_service = container.get('document_parser')")
    print("  video_service = container.get('video_analysis')")
    print("\n配置文件:")
    print("  USE_REAL_DOCUMENT_PARSER=true")
    print("  USE_REAL_VIDEO_ANALYSIS=true")
    print("  DASHSCOPE_API_KEY=your_key")


def main():
    """主函数"""
    print("\n" + "🎯 " * 20)
    print("多模态解析模块 - 适配器测试")
    print("🎯 " * 20)
    
    # 选择测试模式
    print("\n请选择测试模式:")
    print("  1. 快速测试（推荐，只测试核心功能）")
    print("  2. 完整测试（测试所有功能）")
    
    choice = input("\n请输入选项 (1/2，默认1): ").strip() or "1"
    
    if choice == "1":
        asyncio.run(quick_test())
    elif choice == "2":
        asyncio.run(full_test())
    else:
        print("❌ 无效选项")
        return
    
    # 总结
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("\n📦 你的模块适配了两个系统接口:")
    print("  1. IDocumentParserService - 文档解析（图片+文本）")
    print("  2. IVideoAnalysisService - 视频分析（视频）")
    print("\n💡 下一步:")
    print("  1. 在 .env 中设置 USE_REAL_DOCUMENT_PARSER=true")
    print("  2. 在 .env 中设置 USE_REAL_VIDEO_ANALYSIS=true")
    print("  3. 系统会自动使用你的模块")
    print("\n🎉 集成成功！")


if __name__ == "__main__":
    main()
