/**
 * 地板游戏存储服务
 * 使用 localStorage 存储 FloorGame 数据
 */

import { FloorGame } from '../types';
import { imageStorageService } from './imageStorage';

const FLOOR_GAMES_STORAGE_KEY = 'asd_floor_games';

class FloorGameStorageService {
  getAllGames(): FloorGame[] {
    try {
      const data = localStorage.getItem(FLOOR_GAMES_STORAGE_KEY);
      if (!data) return [];

      const games = JSON.parse(data);

      // 数据迁移：将旧的 date 字段转换为 dtstart/dtend
      const migratedGames = games.map((game: any) => {
        if (game.date && !game.dtstart) {
          // 旧数据迁移
          return {
            ...game,
            dtstart: game.date,
            dtend: game.status === 'completed' || game.status === 'aborted' ? game.date : '',
            date: undefined // 删除旧字段
          };
        }
        return game;
      });

      return migratedGames;
    } catch (error) {
      console.error('Failed to load floor games:', error);
      return [];
    }
  }

  saveGame(game: FloorGame): void {
    try {
      const games = this.getAllGames();
      games.push(game);
      // 按 dtstart 倒序
      games.sort((a, b) => new Date(b.dtstart).getTime() - new Date(a.dtstart).getTime());
      localStorage.setItem(FLOOR_GAMES_STORAGE_KEY, JSON.stringify(games));
      // 触发更新事件
      window.dispatchEvent(new CustomEvent('floorGameStatusUpdated'));
    } catch (error) {
      console.error('Failed to save floor game:', error);
      throw new Error('保存地板游戏失败');
    }
  }

  getGameById(id: string): FloorGame | null {
    const games = this.getAllGames();
    return games.find(g => g.id === id) || null;
  }

  updateGame(id: string, updates: Partial<FloorGame>): void {
    try {
      const games = this.getAllGames();
      const index = games.findIndex(g => g.id === id);
      if (index !== -1) {
        games[index] = { ...games[index], ...updates };
        localStorage.setItem(FLOOR_GAMES_STORAGE_KEY, JSON.stringify(games));
        // 触发更新事件
        window.dispatchEvent(new CustomEvent('floorGameStatusUpdated'));
      }
    } catch (error) {
      console.error('Failed to update floor game:', error);
      throw new Error('更新地板游戏失败');
    }
  }

  getRecentGames(count: number): FloorGame[] {
    const games = this.getAllGames();
    return games.slice(0, count);
  }

  deleteGame(id: string): void {
    try {
      const games = this.getAllGames();
      const filtered = games.filter(g => g.id !== id);
      // 清理 IndexedDB 中该游戏的步骤图片
      void imageStorageService.deleteGameImages(id);
      localStorage.setItem(FLOOR_GAMES_STORAGE_KEY, JSON.stringify(filtered));
      // 触发更新事件
      window.dispatchEvent(new CustomEvent('floorGameStatusUpdated'));
    } catch (error) {
      console.error('Failed to delete floor game:', error);
      throw new Error('删除地板游戏失败');
    }
  }
}

export const floorGameStorageService = new FloorGameStorageService();
