/**
 * Account Service
 * 管理用户账号 ID，用于 graphiti 记忆层的多用户隔离
 *
 * - ID 在首次使用时自动生成，持久化到 localStorage
 * - 可在档案页手动修改，修改后历史记忆需重新关联
 * - 退出登录不清除此 ID（Neo4j 数据与 ID 绑定，清除后无法恢复）
 */

export const ACCOUNT_ID_KEY = 'asd_user_account_id';

function generateAccountId(): string {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  const rand = Array.from({ length: 8 }, () =>
    chars[Math.floor(Math.random() * chars.length)]
  ).join('');
  return `user_${rand}`;
}

/** 读取账号 ID，不存在时自动生成并保存 */
export function getAccountId(): string {
  try {
    const saved = localStorage.getItem(ACCOUNT_ID_KEY);
    if (saved) return saved;
    const newId = generateAccountId();
    localStorage.setItem(ACCOUNT_ID_KEY, newId);
    return newId;
  } catch {
    return 'default';
  }
}

/** 手动设置账号 ID，空值时重新生成 */
export function setAccountId(id: string): string {
  const trimmed = id.trim();
  const final = trimmed || generateAccountId();
  localStorage.setItem(ACCOUNT_ID_KEY, final);
  return final;
}
