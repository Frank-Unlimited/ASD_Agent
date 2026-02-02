"""
GraphRAG 数据处理工具
将 docx 文档转换为 txt 格式，供 GraphRAG 索引使用
"""
import os
from pathlib import Path
from docx import Document


def convert_docx_to_txt(input_dir: str, output_dir: str) -> list[str]:
    """
    将目录下所有 docx 文件转换为 txt 格式
    
    Args:
        input_dir: 包含 docx 文件的目录
        output_dir: txt 输出目录
        
    Returns:
        转换成功的文件列表
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    converted_files = []
    
    # 遍历所有 docx 文件（包括子目录）
    for docx_file in input_path.rglob("*.docx"):
        try:
            # 读取 docx
            doc = Document(docx_file)
            
            # 提取所有段落文本
            paragraphs = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            
            # 合并为完整文本
            full_text = "\n\n".join(paragraphs)
            
            # 生成输出文件名（保留原文件名，改扩展名为 .txt）
            output_file = output_path / f"{docx_file.stem}.txt"
            
            # 写入 txt 文件
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            converted_files.append(str(output_file))
            print(f"✅ 转换成功: {docx_file.name} → {output_file.name}")
            
        except Exception as e:
            print(f"❌ 转换失败: {docx_file.name} - {e}")
    
    return converted_files


def main():
    """
    主函数：转换游戏文档
    """
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent
    
    # 定义输入输出路径
    # 输入：原始 docx 文件目录
    docx_input_dir = script_dir / "GraphRAG" / "input" / "3-6岁训练游戏"
    
    # 输出：GraphRAG input 目录（转换后的 txt 直接放在 input 根目录）
    txt_output_dir = script_dir / "GraphRAG" / "input"
    
    print("=" * 60)
    print("🔄 开始转换 docx → txt")
    print(f"📂 输入目录: {docx_input_dir}")
    print(f"📁 输出目录: {txt_output_dir}")
    print("=" * 60)
    
    if not docx_input_dir.exists():
        print(f"❌ 输入目录不存在: {docx_input_dir}")
        return
    
    # 执行转换
    converted = convert_docx_to_txt(str(docx_input_dir), str(txt_output_dir))
    
    print("=" * 60)
    print(f"✅ 转换完成！共处理 {len(converted)} 个文件")
    print("=" * 60)
    
    # 列出生成的文件
    if converted:
        print("\n📄 生成的文件:")
        for f in converted:
            print(f"   - {Path(f).name}")


if __name__ == "__main__":
    main()
