/**
 * 多模态分析服务（前端版）
 * 功能：图片分析、视频分析、文本分析
 */

import { dashscopeClient } from './dashscopeClient';
import { fileUploadService, FileMetadata } from './fileUpload';

export interface AnalysisResult {
  success: boolean;
  content: string;
  metadata?: FileMetadata;
  error?: string;
}

class MultimodalService {
  /**
   * 分析图片
   */
  async parseImage(file: File, prompt?: string): Promise<AnalysisResult> {
    try {
      // 1. 处理文件
      const metadata = await fileUploadService.processFile(file);

      // 2. 构建分析提示词
      const analysisPrompt = prompt || this.getDefaultImagePrompt();

      // 3. 调用 DashScope API
      const content = await dashscopeClient.analyzeImage(metadata.base64!, analysisPrompt);

      return {
        success: true,
        content,
        metadata
      };
    } catch (error) {
      console.error('Image analysis failed:', error);
      return {
        success: false,
        content: '',
        error: error instanceof Error ? error.message : '图片分析失败'
      };
    }
  }

  /**
   * 分析视频
   */
  async parseVideo(file: File, prompt?: string): Promise<AnalysisResult> {
    try {
      // 1. 处理文件
      const metadata = await fileUploadService.processFile(file);

      // 2. 构建分析提示词
      const analysisPrompt = prompt || this.getDefaultVideoPrompt();

      // 3. 调用 DashScope API
      const content = await dashscopeClient.analyzeVideo(metadata.base64!, analysisPrompt);

      return {
        success: true,
        content,
        metadata
      };
    } catch (error) {
      console.error('Video analysis failed:', error);
      return {
        success: false,
        content: '',
        error: error instanceof Error ? error.message : '视频分析失败'
      };
    }
  }

  /**
   * 分析文本
   */
  async parseText(text: string, prompt?: string): Promise<AnalysisResult> {
    try {
      const fullPrompt = prompt ? `${prompt}\n\n${text}` : text;
      const content = await dashscopeClient.chat(fullPrompt);

      return {
        success: true,
        content
      };
    } catch (error) {
      console.error('Text analysis failed:', error);
      return {
        success: false,
        content: '',
        error: error instanceof Error ? error.message : '文本分析失败'
      };
    }
  }

  /**
   * 获取默认图片分析提示词
   */
  private getDefaultImagePrompt(): string {
    return `请作为一名专业的 ASD 儿童行为分析师，详细分析这张图片：

1. **场景描述**：图片中的环境和场景
2. **人物识别**：识别图片中的人物（儿童、家长、治疗师等）
3. **活动内容**：正在进行的活动或游戏
4. **物品识别**：涉及的玩具、物品、教具
5. **行为分析**：
   - 孩子的姿势和动作
   - 面部表情和情绪状态
   - 注意力集中程度
   - 与他人的互动情况
6. **兴趣维度**：根据图片内容，推测孩子可能的兴趣点（视觉、听觉、触觉、运动、建构、秩序、社交、探索）
7. **发展评估**：从图片中可以观察到的发展能力（精细动作、大运动、社交、语言、认知等）

请用结构化的方式输出分析结果。`;
  }

  /**
   * 获取默认视频分析提示词
   */
  private getDefaultVideoPrompt(): string {
    return `请作为一名专业的 ASD 儿童行为分析师，详细分析这个视频：

1. **场景描述**：视频中的环境和场景
2. **时间线分析**：视频中的关键时刻和事件
3. **人物互动**：儿童与他人的互动过程
4. **活动流程**：活动的开始、进行、结束
5. **行为观察**：
   - 孩子的动作和姿势变化
   - 情绪状态的变化
   - 注意力的持续时间
   - 主动性和参与度
6. **互动质量**：
   - 眼神接触
   - 轮流互动
   - 情感共鸣
   - 沟通方式
7. **兴趣和能力**：展现出的兴趣点和发展能力
8. **建议**：基于观察的干预建议

请用结构化的方式输出分析结果。`;
  }
}

// 导出单例
export const multimodalService = new MultimodalService();
