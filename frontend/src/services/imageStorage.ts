/**
 * IndexedDB 图片存储服务
 * 用于存储地板游戏步骤的生成插画（base64 dataUrl）
 * localStorage 空间有限（5-10MB），不适合存图片，所以用 IndexedDB
 */

const DB_NAME = 'asd_floor_game_images';
const STORE_NAME = 'step_images';
const DB_VERSION = 1;

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME);
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function buildKey(gameId: string, stepIndex: number): string {
  return `${gameId}_step_${stepIndex}`;
}

class ImageStorageService {
  async saveStepImage(gameId: string, stepIndex: number, dataUrl: string): Promise<void> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      tx.objectStore(STORE_NAME).put(dataUrl, buildKey(gameId, stepIndex));
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = () => { db.close(); reject(tx.error); };
    });
  }

  async getStepImage(gameId: string, stepIndex: number): Promise<string | undefined> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readonly');
      const req = tx.objectStore(STORE_NAME).get(buildKey(gameId, stepIndex));
      req.onsuccess = () => { db.close(); resolve(req.result as string | undefined); };
      req.onerror = () => { db.close(); reject(req.error); };
    });
  }

  async getGameImages(gameId: string): Promise<Map<number, string>> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const result = new Map<number, string>();
      const tx = db.transaction(STORE_NAME, 'readonly');
      const store = tx.objectStore(STORE_NAME);
      const request = store.openCursor();
      const prefix = `${gameId}_step_`;

      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          const key = cursor.key as string;
          if (key.startsWith(prefix)) {
            const stepIndex = parseInt(key.slice(prefix.length), 10);
            result.set(stepIndex, cursor.value as string);
          }
          cursor.continue();
        } else {
          db.close();
          resolve(result);
        }
      };
      request.onerror = () => { db.close(); reject(request.error); };
    });
  }

  async deleteGameImages(gameId: string): Promise<void> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const request = store.openCursor();
      const prefix = `${gameId}_step_`;

      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          if ((cursor.key as string).startsWith(prefix)) {
            cursor.delete();
          }
          cursor.continue();
        }
      };
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = () => { db.close(); reject(tx.error); };
    });
  }
}

export const imageStorageService = new ImageStorageService();
