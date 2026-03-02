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
        timestamp: new Date(msg.timestamp),
        searchResults: msg.searchResults || undefined  // 保留搜索结果
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
    const greetings = [
      "嗨，很高兴见到你！我是你的地板时光伙伴 🌟\n\n我看了孩子最近的情况，咱们今天想聊点什么？",
      "你好呀！我已经准备好了 ✨\n\n看了孩子的档案，感觉今天可以有不少收获。想从哪里开始？",
      "欢迎回来！👋\n\n我刚温习了孩子的成长记录，有什么想一起探讨的吗？",
      "Hi！地板时光助手在线 🎯\n\n孩子的档案我都看过了，今天想重点关注哪方面呢？",
      "你来啦！很开心能陪伴你们 💫\n\n我已经了解了孩子的最新状态，咱们聊聊接下来的计划？"
    ];

    // 随机选择一条欢迎语
    const randomGreeting = greetings[Math.floor(Math.random() * greetings.length)];

    return [
      {
        id: '1',
        role: 'model',
        text: randomGreeting,
        timestamp: new Date()
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
