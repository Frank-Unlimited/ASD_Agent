/**
 * 清空所有缓存数据
 */

export const clearAllCache = () => {
  const keys = [
    'asd_comprehensive_assessments',
    'asd_game_recommendations',
    'asd_behavior_analyses',
    'asd_game_evaluations',
    'asd_floortime_medical_reports',
    'asd_floortime_child_profile',
    'asd_floortime_chat_history',
    'asd_floortime_behavior_logs',
    'asd_floor_games'
  ];
  
  keys.forEach(key => {
    localStorage.removeItem(key);
  });
  
  console.log('✅ 所有缓存数据已清空');
};

// 在浏览器控制台可用
if (typeof window !== 'undefined') {
  (window as any).clearAllCache = clearAllCache;
  console.log('清空缓存函数已加载: window.clearAllCache()');
}
