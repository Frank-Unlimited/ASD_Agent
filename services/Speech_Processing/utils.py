"""
工具函数模块
"""
import os
import subprocess
from typing import Optional


def convert_audio_to_pcm(
    input_path: str,
    output_path: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1
) -> str:
    """
    将音频文件转换为PCM格式
    
    Args:
        input_path: 输入音频文件路径（支持mp3, wav, m4a等）
        output_path: 输出PCM文件路径（可选）
        sample_rate: 采样率（默认16000Hz）
        channels: 声道数（默认1，单声道）
        
    Returns:
        str: 输出PCM文件路径
        
    Raises:
        Exception: 转换失败
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    
    # 如果没有指定输出路径，自动生成
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.pcm"
    
    # 检查是否已经是PCM格式
    if input_path.lower().endswith('.pcm'):
        return input_path
    
    # 尝试使用 ffmpeg 转换
    try:
        # ffmpeg 命令：转换为PCM格式
        cmd = [
            'ffmpeg',
            '-i', input_path,           # 输入文件
            '-f', 's16le',              # 格式：16位小端PCM
            '-acodec', 'pcm_s16le',     # 编码：PCM 16位
            '-ar', str(sample_rate),    # 采样率
            '-ac', str(channels),       # 声道数
            '-y',                       # 覆盖输出文件
            output_path                 # 输出文件
        ]
        
        # 执行转换
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        if os.path.exists(output_path):
            return output_path
        else:
            raise Exception("转换失败：输出文件未生成")
    
    except FileNotFoundError:
        raise Exception(
            "ffmpeg 未安装。请安装 ffmpeg:\n"
            "Windows: choco install ffmpeg 或从 https://ffmpeg.org/ 下载\n"
            "Mac: brew install ffmpeg\n"
            "Linux: sudo apt-get install ffmpeg"
        )
    
    except subprocess.CalledProcessError as e:
        raise Exception(f"ffmpeg 转换失败: {e.stderr.decode()}")


def get_audio_info(file_path: str) -> dict:
    """
    获取音频文件信息
    
    Args:
        file_path: 音频文件路径
        
    Returns:
        dict: 音频信息（格式、采样率、时长等）
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        import json
        info = json.loads(result.stdout.decode())
        
        # 提取音频流信息
        audio_stream = None
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break
        
        if audio_stream:
            return {
                'format': info.get('format', {}).get('format_name', 'unknown'),
                'duration': float(info.get('format', {}).get('duration', 0)),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'codec': audio_stream.get('codec_name', 'unknown'),
                'bit_rate': int(audio_stream.get('bit_rate', 0))
            }
        else:
            return {'error': '未找到音频流'}
    
    except FileNotFoundError:
        return {'error': 'ffprobe 未安装'}
    
    except Exception as e:
        return {'error': str(e)}


def is_ffmpeg_available() -> bool:
    """
    检查 ffmpeg 是否可用
    
    Returns:
        bool: True 如果 ffmpeg 可用
    """
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except:
        return False
