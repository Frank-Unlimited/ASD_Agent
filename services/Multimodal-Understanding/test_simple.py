"""
简化版测试 - 只使用三个核心接口
"""
import os

# 从环境变量读取API密钥（不再硬编码）
# 请在 .env 文件中设置 DASHSCOPE_API_KEY
if not os.getenv("DASHSCOPE_API_KEY"):
    print("❌ 错误: 未设置 DASHSCOPE_API_KEY 环境变量")
    print("请在项目根目录的 .env 文件中设置:")
    print("DASHSCOPE_API_KEY=your_api_key_here")
    exit(1)

from api_interface import parse_text, parse_image, parse_video
from utils import encode_local_image, encode_local_video

# 本地文件路径（可修改）
LOCAL_IMAGE_PATH = r"E:\pro\aa.jpg"
LOCAL_VIDEO_PATH = r"E:\pro\bb.mp4"

print("=" * 60)
print("测试1: 文本输入")
print("=" * 60)

result = parse_text("什么是人工智能？")
print(f"\n输入: 什么是人工智能？")
print(f"输出: {result[:200]}...")  # 只显示前200字符

print("\n" + "=" * 60)
print("测试2: 图片输入（URL）")
print("=" * 60)

result = parse_image(
    "https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg",
    "这道题怎么解答？"
)
print(f"\n输入: 图片URL + 问题")
print(f"输出: {result[:200]}...")  # 只显示前200字符

print("\n" + "=" * 60)
print("测试3: 图片输入（本地文件base64）")
print("=" * 60)

try:
    if not os.path.exists(LOCAL_IMAGE_PATH):
        print(f"\n⚠️  跳过: 图片文件不存在 - {LOCAL_IMAGE_PATH}")
        print("提示: 修改 LOCAL_IMAGE_PATH 为实际图片路径")
    else:
        print(f"\n图片路径: {LOCAL_IMAGE_PATH}")
        print("正在编码为base64...")
        image_base64 = encode_local_image(LOCAL_IMAGE_PATH)
        print(f"✅ 编码成功，长度: {len(image_base64)} 字符")
        
        print("正在识别...")
        result = parse_image(image_base64, "请详细描述这张图片的内容")
        print(f"\n输入: 本地图片 + 问题")
        print(f"输出: {result}")
except Exception as e:
    print(f"\n❌ 错误: {e}")

print("\n" + "=" * 60)
print("测试4: 视频输入（URL）")
print("=" * 60)

try:
    video_url = "https://media.w3.org/2010/05/sintel/trailer.mp4"
    print(f"\n视频URL: {video_url}")
    print("正在识别...(这可能需要一些时间)")
    result = parse_video(video_url, "请详细描述视频中的场景、人物、动作和故事情节")
    print(f"\n输入: 视频URL + 问题")
    print(f"输出: {result}")
except Exception as e:
    print(f"\n❌ 错误: {e}")

print("\n" + "=" * 60)
print("测试5: 视频输入（本地文件base64）")
print("=" * 60)

try:
    if not os.path.exists(LOCAL_VIDEO_PATH):
        print(f"\n⚠️  跳过: 视频文件不存在 - {LOCAL_VIDEO_PATH}")
        print("提示: 修改 LOCAL_VIDEO_PATH 为实际视频路径")
    else:
        print(f"\n视频路径: {LOCAL_VIDEO_PATH}")
        print("正在编码为base64...")
        video_base64 = encode_local_video(LOCAL_VIDEO_PATH)
        print(f"✅ 编码成功，长度: {len(video_base64)} 字符")
        
        print("正在识别...")
        result = parse_video(video_base64, "请总结视频的主要内容和场景")
        print(f"\n输入: 本地视频 + 问题")
        print(f"输出: {result}")
except Exception as e:
    print(f"\n❌ 错误: {e}")

print("\n" + "=" * 60)
print("完成！")
print("=" * 60)
print("\n📦 核心接口:")
print("1. parse_text(text, prompt) -> str")
print("2. parse_image(image_url, prompt) -> str")
print("3. parse_video(video_url, prompt) -> str")
print("\n🔧 辅助函数:")
print("- encode_local_image(path) -> base64_str")
print("- encode_local_video(path) -> base64_str")
print("\n💡 使用提示:")
print("- 修改 LOCAL_IMAGE_PATH 和 LOCAL_VIDEO_PATH 为你的文件路径")
print("- URL和base64两种方式都支持")
