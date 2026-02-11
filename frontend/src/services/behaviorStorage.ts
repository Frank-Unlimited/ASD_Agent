/**
 * 行为存储服务
 * 使用 localStorage 存储行为分析数据
 */

import { BehaviorAnalysis } from '../types';

const BEHAVIORS_STORAGE_KEY = 'asd_floortime_behaviors';

class BehaviorStorageService {
  /**
   * 获取所有行为记录
   */
  getAllBehaviors(): BehaviorAnalysis[] {
    try {
      const data = localStorage.getItem(BEHAVIORS_STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to load behaviors:', error);
      return [];
    }
  }

  /**
   * 保存行为记录
   */
  saveBehavior(behavior: BehaviorAnalysis): void {
    try {
      const behaviors = this.getAllBehaviors();
      
      // 添加时间戳和ID
      const behaviorWithMeta: BehaviorAnalysis = {
        ...behavior,
        id: behavior.id || this.generateBehaviorId(),
        timestamp: behavior.timestamp || new Date().toISOString()
      };
      
      behaviors.push(behaviorWithMeta);
      
      // 按时间倒序排列（最新的在前）
      behaviors.sort((a, b) => 
        new Date(b.timestamp || 0).getTime() - new Date(a.timestamp || 0).getTime()
      );
      
      localStorage.setItem(BEHAVIORS_STORAGE_KEY, JSON.stringify(behaviors));
    } catch (error) {
      console.error('Failed to save behavior:', error);
      throw new Error('保存行为记录失败');
    }
  }

  /**
   * 批量保存行为记录
   */
  saveBehaviors(behaviors: BehaviorAnalysis[]): void {
    behaviors.forEach(behavior => this.saveBehavior(behavior));
  }

  /**
   * 根据 ID 删除行为记录
   */
  deleteBehavior(id: string): void {
    try {
      const behaviors = this.getAllBehaviors();
      const filtered = behaviors.filter(b => b.id !== id);
      localStorage.setItem(BEHAVIORS_STORAGE_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete behavior:', error);
      throw new Error('删除行为记录失败');
    }
  }

  /**
   * 根据来源筛选行为记录
   */
  getBehaviorsBySource(source: 'GAME' | 'REPORT' | 'CHAT'): BehaviorAnalysis[] {
    const behaviors = this.getAllBehaviors();
    return behaviors.filter(b => b.source === source);
  }

  /**
   * 根据兴趣维度筛选行为记录
   */
  getBehaviorsByDimension(dimension: string): BehaviorAnalysis[] {
    const behaviors = this.getAllBehaviors();
    return behaviors.filter(b => 
      b.matches.some(m => m.dimension === dimension)
    );
  }

  /**
   * 获取最近N条行为记录
   */
  getRecentBehaviors(count: number = 10): BehaviorAnalysis[] {
    const behaviors = this.getAllBehaviors();
    return behaviors.slice(0, count);
  }

  /**
   * 清空所有行为记录
   */
  clearAllBehaviors(): void {
    try {
      localStorage.removeItem(BEHAVIORS_STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear behaviors:', error);
    }
  }

  /**
   * 生成行为记录 ID
   */
  generateBehaviorId(): string {
    return `behavior_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 获取统计信息
   */
  getStatistics() {
    const behaviors = this.getAllBehaviors();
    const dimensionCounts: Record<string, number> = {};
    const sourceCounts: Record<string, number> = {};
    
    behaviors.forEach(behavior => {
      // 统计来源
      if (behavior.source) {
        sourceCounts[behavior.source] = (sourceCounts[behavior.source] || 0) + 1;
      }
      
      // 统计兴趣维度
      behavior.matches.forEach(match => {
        dimensionCounts[match.dimension] = (dimensionCounts[match.dimension] || 0) + 1;
      });
    });
    
    return {
      total: behaviors.length,
      dimensionCounts,
      sourceCounts,
      latestTimestamp: behaviors[0]?.timestamp
    };
  }
}

// 导出单例
export const behaviorStorageService = new BehaviorStorageService();
