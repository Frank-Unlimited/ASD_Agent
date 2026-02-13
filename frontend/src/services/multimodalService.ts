/**
 * 多模态分析服务（前端版）
 * 功能：图片分析、视频分析、文本分析
 */

import { dashscopeClient } from './dashscopeClient';
import { fileUploadService, FileMetadata } from './fileUpload';
import { DEFAULT_IMAGE_ANALYSIS_PROMPT, DEFAULT_VIDEO_ANALYSIS_PROMPT } from '../prompts';

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
  async parseImage(file: File, prompt?: string, useJsonFormat: boolean = false): Promise<AnalysisResult> {
    try {
      // 1. 处理文件
      const metadata = await fileUploadService.processFile(file);

      // 2. 构建分析提示词
      const analysisPrompt = prompt || this.getDefaultImagePrompt();

      // 3. 调用 DashScope API
      const content = await dashscopeClient.analyzeImage(metadata.base64!, analysisPrompt, useJsonFormat);

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
    return DEFAULT_IMAGE_ANALYSIS_PROMPT;
  }

  /**
   * 获取默认视频分析提示词
   */
  private getDefaultVideoPrompt(): string {
    return DEFAULT_VIDEO_ANALYSIS_PROMPT;
  }
}

// 导出单例
export const multimodalService = new MultimodalService();
