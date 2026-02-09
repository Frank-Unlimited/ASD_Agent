# 快速参考指南

## 📂 文件位置速查

### 需要修改 UI？
- **主应用**: `src/App.tsx`
- **样式配置**: `index.html` (Tailwind 配置)

### 需要修改数据？
- **类型定义**: `src/types/index.ts`
- **Mock 数据**: `src/constants/mockData.ts`
- **初始值**: `src/constants/mockData.ts`

### 需要修改 AI 功能？
- **报告分析 Prompt**: `src/prompts/asd-report-analysis.ts`
- **多模态服务**: `src/services/multimodalService.ts`
- **DashScope 客户端**: `src/services/dashscopeClient.ts`

### 需要修改存储？
- **报告存储**: `src/services/reportStorage.ts`
- **文件上传**: `src/services/fileUpload.ts`

### 需要修改工具函数？
- **辅助函数**: `src/utils/helpers.ts`

## 🔑 关键函数速查

### 计算年龄
```typescript
import { calculateAge } from './utils/helpers';
const age = calculateAge('2020-01-01'); // 返回年龄
```

### 获取兴趣维度配置
```typescript
import { getDimensionConfig } from './utils/helpers';
const config = getDimensionConfig('Visual');
// 返回: { icon, color, label }
```

### 格式化时间
```typescript
import { formatTime } from './utils/helpers';
const time = formatTime(125); // 返回 "2:05"
```

### 报告存储操作
```typescript
import { reportStorageService } from './services/reportStorage';

// 保存报告
reportStorageService.saveReport(report);

// 获取所有报告
const reports = reportStorageService.getAllReports();

// 获取最新报告
const latest = reportStorageService.getLatestReport();

// 删除报告
reportStorageService.deleteReport(reportId);

// 清空所有报告
reportStorageService.clearAllReports();
```

### 多模态分析
```typescript
import { multimodalService } from './services/multimodalService';

// 分析图片
const result = await multimodalService.parseImage(
  file, 
  prompt, 
  useJsonFormat
);

// 分析视频
const result = await multimodalService.parseVideo(file, prompt);

// 分析文本
const result = await multimodalService.parseText(text, prompt);
```

## 🎨 常用组件模式

### 页面组件结构
```typescript
const PageExample = ({ prop1, prop2 }: { prop1: Type1, prop2: Type2 }) => {
  const [state, setState] = useState<Type>(initialValue);
  
  useEffect(() => {
    // 副作用
  }, [dependencies]);
  
  return (
    <div className="p-4 space-y-6 h-full overflow-y-auto bg-background">
      {/* 内容 */}
    </div>
  );
};
```

### 弹窗组件模式
```typescript
const Modal = ({ onClose }: { onClose: () => void }) => (
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
    <div className="bg-white rounded-2xl max-w-2xl w-full" onClick={(e) => e.stopPropagation()}>
      {/* 内容 */}
    </div>
  </div>
);
```

## 🎯 常用样式类

### 布局
- `p-4`: padding 1rem
- `space-y-4`: 垂直间距 1rem
- `flex items-center justify-between`: Flex 布局
- `grid grid-cols-2 gap-4`: Grid 布局

### 卡片
- `bg-white rounded-xl shadow-sm border border-gray-100`
- `bg-gradient-to-br from-green-50 to-blue-50`

### 按钮
- `bg-primary text-white py-3 rounded-xl font-bold hover:bg-green-600 transition`
- `bg-white text-gray-700 border border-gray-200 hover:bg-gray-50`

### 文本
- `text-sm font-bold text-gray-700`: 小标题
- `text-xs text-gray-500`: 辅助文本
- `text-2xl font-bold text-gray-800`: 大标题

## 🔄 数据流速查

### 儿童档案数据流
```
用户输入 → PageWelcome → localStorage → App State → 所有页面
```

### 报告分析数据流
```
上传图片 → multimodalService → DashScope API → 解析 JSON → reportStorage → PageProfile
```

### 游戏评估数据流
```
游戏互动 → 记录日志 → api.analyzeSession → 更新兴趣/能力 → localStorage
```

## 🐛 常见问题

### Q: 修改后页面没有更新？
A: 检查 localStorage 是否需要清空，或者退出登录重新进入

### Q: 类型错误？
A: 检查 `src/types/index.ts` 中的类型定义是否正确

### Q: 导入路径错误？
A: 确保使用相对路径，从 `src/` 开始

### Q: AI 返回格式不对？
A: 检查 `src/prompts/asd-report-analysis.ts` 中的 Prompt 是否正确

### Q: 报告保存失败？
A: 检查 localStorage 是否已满（通常限制 5-10MB）

## 📱 开发技巧

### 快速调试
1. 打开浏览器控制台（F12）
2. 查看 Console 标签页的日志
3. 查看 Application → Local Storage 查看存储数据

### 清空数据
```javascript
// 在浏览器控制台执行
localStorage.clear();
location.reload();
```

### 查看存储的报告
```javascript
// 在浏览器控制台执行
JSON.parse(localStorage.getItem('asd_floortime_medical_reports'));
```

### 查看儿童档案
```javascript
// 在浏览器控制台执行
JSON.parse(localStorage.getItem('asd_floortime_child_profile'));
```

## 🚀 性能优化建议

1. **图片优化**: 报告图片使用 base64 存储，注意大小限制
2. **懒加载**: 大组件考虑使用 React.lazy
3. **Memo 优化**: 频繁渲染的组件使用 React.memo
4. **虚拟滚动**: 长列表考虑使用虚拟滚动

## 📚 学习资源

- [React 官方文档](https://react.dev/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Tailwind CSS 文档](https://tailwindcss.com/)
- [Vite 官方文档](https://vitejs.dev/)
