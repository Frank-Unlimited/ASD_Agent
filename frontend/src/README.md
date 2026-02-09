# 前端项目结构说明

## 目录结构

```
src/
├── components/          # UI 组件
│   ├── pages/          # 页面组件（待拆分）
│   ├── layout/         # 布局组件（待拆分）
│   └── common/         # 通用组件（待拆分）
├── services/           # 服务层
│   ├── api.ts         # API 服务
│   ├── dashscopeClient.ts  # 阿里云 DashScope 客户端
│   ├── fileUpload.ts  # 文件上传服务
│   ├── geminiService.ts    # Google Gemini 服务
│   ├── multimodalService.ts # 多模态分析服务
│   ├── reportStorage.ts    # 报告存储服务
│   └── speechService.ts    # 语音服务
├── prompts/            # AI Prompts
│   └── asd-report-analysis.ts  # ASD 报告分析 Prompt
├── types/              # TypeScript 类型定义
│   └── index.ts       # 所有类型定义
├── utils/              # 工具函数
│   └── helpers.ts     # 通用辅助函数
├── constants/          # 常量定义
│   └── mockData.ts    # Mock 数据和初始值
├── App.tsx             # 主应用组件
└── main.tsx            # 应用入口文件
```

## 模块说明

### Services（服务层）
- **api.ts**: 后端 API 调用封装
- **dashscopeClient.ts**: 阿里云通义千问多模态模型客户端
- **fileUpload.ts**: 文件上传和处理服务
- **multimodalService.ts**: 图片、视频、文本分析服务
- **reportStorage.ts**: 医疗报告本地存储管理
- **speechService.ts**: 语音识别和合成服务

### Types（类型定义）
- 所有 TypeScript 接口和类型定义
- 包括：Page、Game、ChildProfile、MedicalReport 等

### Utils（工具函数）
- **helpers.ts**: 
  - `getDimensionConfig()`: 获取兴趣维度配置
  - `calculateAge()`: 计算年龄
  - `formatTime()`: 格式化时间
  - `getInterestLevel()`: 获取兴趣等级

### Constants（常量）
- **mockData.ts**:
  - `MOCK_GAMES`: 游戏库数据
  - `WEEK_DATA`: 日历数据
  - `INITIAL_TREND_DATA`: 初始趋势数据
  - `INITIAL_INTEREST_SCORES`: 初始兴趣分数
  - `INITIAL_ABILITY_SCORES`: 初始能力分数

### Prompts（AI 提示词）
- **asd-report-analysis.ts**: ASD 医疗报告分析的 AI Prompt

## 待优化

当前 `App.tsx` 文件较大（约 1700 行），包含所有页面组件。后续可以进一步拆分：

1. **页面组件拆分** (`components/pages/`)
   - `PageWelcome.tsx` - 欢迎引导页
   - `PageProfile.tsx` - 儿童档案页
   - `PageChat.tsx` - AI 对话页
   - `PageCalendar.tsx` - 成长日历页
   - `PageGames.tsx` - 游戏库页

2. **布局组件拆分** (`components/layout/`)
   - `Sidebar.tsx` - 侧边栏
   - `Header.tsx` - 顶部导航
   - `BottomNav.tsx` - 底部导航

3. **通用组件拆分** (`components/common/`)
   - `ReportDetailModal.tsx` - 报告详情弹窗
   - `LogoutConfirmModal.tsx` - 退出确认弹窗
   - 等等

## 开发规范

1. **导入顺序**:
   - React 相关
   - 第三方库
   - 类型定义
   - 服务
   - 常量和工具

2. **文件命名**:
   - 组件: PascalCase (如 `PageProfile.tsx`)
   - 服务/工具: camelCase (如 `reportStorage.ts`)
   - 常量: camelCase (如 `mockData.ts`)

3. **类型定义**:
   - 所有类型统一在 `types/index.ts` 中定义
   - 避免在组件中定义类型

4. **状态管理**:
   - 当前使用 React useState
   - 复杂状态可考虑引入 Context API 或状态管理库
