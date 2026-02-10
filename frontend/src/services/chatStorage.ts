/**
 * 聊天历史存储服务
 * 使用 localStorage 存储聊天消息
 */

import { ChatMessage } from '../types';

const CHAT_HISTORY_KEY = 'asd_floortime_chat_history';
const MAX_MESSAGES = 100; // 最多保存 100 条消息

class ChatStorageService {
  /**
   * 获取聊天历史
   */
  getChatHistory(): ChatMessage[] {
    try {
      const data = localStorage.getItem(CHAT_HISTORY_KEY);
      if (!data) return this.getDefaultMessages();
      
      const messages = JSON.parse(data);
      
      // 转换 timestamp 为 Date 对象
      return messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }));
    } catch (error) {
      console.error('Failed to load chat history:', error);
      return this.getDefaultMessages();
    }
  }

  /**
   * 保存聊天历史
   */
  saveChatHistory(messages: ChatMessage[]): void {
    try {
      // 只保留最近的消息
      const messagesToSave = messages.slice(-MAX_MESSAGES);
      
      // 转换 Date 对象为 ISO 字符串
      const serializedMessages = messagesToSave.map(msg => ({
        ...msg,
        timestamp: msg.timestamp.toISOString()
      }));
      
      localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(serializedMessages));
    } catch (error) {
      console.error('Failed to save chat history:', error);
    }
  }

  /**
   * 添加消息到历史
   */
  addMessage(message: ChatMessage): void {
    const history = this.getChatHistory();
    history.push(message);
    this.saveChatHistory(history);
  }

  /**
   * 批量添加消息
   */
  addMessages(messages: ChatMessage[]): void {
    const history = this.getChatHistory();
    history.push(...messages);
    this.saveChatHistory(history);
  }

  /**
   * 清空聊天历史
   */
  clearChatHistory(): void {
    try {
      localStorage.removeItem(CHAT_HISTORY_KEY);
    } catch (error) {
      console.error('Failed to clear chat history:', error);
    }
  }

  /**
   * 获取默认欢迎消息
   */
  getDefaultMessages(): ChatMessage[] {
    return [
      { 
        id: '1', 
        role: 'model', 
        text: "**你好！我是地板时光助手。** 👋 \n\n我已读取了孩子的最新档案。今天我们重点关注什么？", 
        timestamp: new Date(),
        options: ["🎮 推荐今日游戏", "📝 记录刚才的互动", "🤔 咨询孩子行为问题", "📅 查看本周计划"] 
      }
    ];
  }

  /**
   * 重置为默认消息
   */
  resetToDefault(): void {
    this.saveChatHistory(this.getDefaultMessages());
  }
}

// 导出单例
export const chatStorageService = new ChatStorageService();
