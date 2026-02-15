/**
 * 地板游戏存储服务
 * 使用 localStorage 存储 FloorGame 数据
 */

import { FloorGame } from '../types';

const FLOOR_GAMES_STORAGE_KEY = 'asd_floor_games';

class FloorGameStorageService {
  getAllGames(): FloorGame[] {
    try {
      const data = localStorage.getItem(FLOOR_GAMES_STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to load floor games:', error);
      return [];
    }
  }

  saveGame(game: FloorGame): void {
    try {
      const games = this.getAllGames();
      games.push(game);
      // 按 date 倒序
      games.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      localStorage.setItem(FLOOR_GAMES_STORAGE_KEY, JSON.stringify(games));
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
      localStorage.setItem(FLOOR_GAMES_STORAGE_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete floor game:', error);
      throw new Error('删除地板游戏失败');
    }
  }
}

export const floorGameStorageService = new FloorGameStorageService();
