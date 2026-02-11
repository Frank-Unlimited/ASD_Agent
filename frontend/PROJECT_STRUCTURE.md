# ASD 儿童地板时光助手 - 前端项目结构

## 📁 项目目录结构

```
frontend/
├── src/                        # 源代码目录
│   ├── components/            # UI 组件
│   │   ├── pages/            # 页面组件（待拆分）
│   │   ├── layout/           # 布局组件（待拆分）
│   │   └── common/           # 通用组件（待拆分）
│   ├── services/             # 服务层
│   │   ├── api.ts           # 后端 API 服务
│   │   ├── dashscopeClient.ts    # 阿里云 DashScope 客户端
│   │   ├── fileUpload.ts    # 文件上传服务
│   │   ├── geminiService.ts # Google Gemini 服务
│   │   ├── multimodalService.ts  # 多模态分析服务
│   │   ├── reportStorage.ts # 报告存储服务
│   │   └── speechService.ts # 语音服务
│   ├── prompts/              # AI Prompts
│   │   └── asd-report-analysis.ts  # ASD 报告分析 Prompt
│   ├── types/                # TypeScript 类型定义
│   │   └── index.ts         # 所有类型定义
│   ├── utils/                # 工具函数
│   │   └── helpers.ts       # 通用辅助函数
│   ├── constants/            # 常量定义
│   │   └── mockData.ts      # Mock 数据和初始值
│   ├── App.tsx               # 主应用组件
│   ├── main.tsx              # 应用入口文件
│   └── README.md             # 源代码说明文档
├── .env                       # 环境变量配置
├── .env.example              # 环境变量示例
├── index.html                # HTML 入口文件
├── package.json              # 项目依赖配置
├── tsconfig.json             # TypeScript 配置
├── vite.config.ts            # Vite 配置
└── PROJECT_STRUCTURE.md      # 本文档
```

## 🎯 核心功能模块

### 1. 欢迎引导页 (PageWelcome)
- **功能**: 新用户引导，收集儿童基本信息
- **步骤**:
  1. 收集基本信息（姓名、性别、出生日期）
  2. 可选：上传医疗报告或口述情况
- **相关文件**:
  - `App.tsx` (PageWelcome 组件)
  - `services/multimodalService.ts` (报告分析)
  - `prompts/asd-report-analysis.ts` (分析 Prompt)

### 2. 儿童档案页 (PageProfile)
- **功能**: 查看儿童信息、最新画像、报告历史
- **特性**:
  - 显示头像和基本信息
  - 显示最新孩子画像
  - 查看报告列表
  - 导入/导出报告
- **相关文件**:
  - `App.tsx` (PageProfile 组件)
  - `services/reportStorage.ts` (报告存储)
  - `types/index.ts` (MedicalReport 类型)

### 3. AI 对话助手 (PageAIChat)
- **功能**: 与 AI 对话，获取干预建议
- **特性**:
  - 智能对话
  - 快捷选项
  - 上下文理解
- **相关文件**:
  - `App.tsx` (PageAIChat 组件)
  - `services/api.ts` (对话 API)

### 4. 成长日历 (PageCalendar)
- **功能**: 查看每周游戏计划
- **特性**:
  - 周视图
  - 游戏推荐
  - 完成记录
- **相关文件**:
  - `App.tsx` (PageCalendar 组件)
  - `constants/mockData.ts` (WEEK_DATA)

### 5. 游戏库 (PageGames)
- **功能**: 浏览和执行地板时光游戏
- **特性**:
  - 游戏列表
  - 游戏执行
  - 互动记录
  - 游戏总结
- **相关文件**:
  - `App.tsx` (PageGames 组件)
  - `constants/mockData.ts` (MOCK_GAMES)
  - `services/api.ts` (游戏分析)

## 🔧 技术栈

### 核心框架
- **React 19**: UI 框架
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Tailwind CSS**: 样式框架

### UI 组件库
- **Lucide React**: 图标库
- **Recharts**: 图表库
- **React Markdown**: Markdown 渲染

### AI 服务
- **阿里云 DashScope**: 多模态分析（通义千问）
- **Google Gemini**: 备用 AI 服务

### 数据存储
- **LocalStorage**: 本地数据持久化
  - 儿童档案
  - 医疗报告
  - 兴趣/能力数据

## 📊 数据流

```
用户输入 → 服务层 → AI 处理 → 数据存储 → UI 更新
   ↓
LocalStorage
```

### 数据存储键值
- `asd_floortime_child_profile`: 儿童档案
- `asd_floortime_medical_reports`: 医疗报告列表
- `asd_floortime_interest_profile`: 兴趣档案
- `asd_floortime_ability_profile`: 能力档案

## 🚀 开发指南

### 环境配置
1. 复制 `.env.example` 为 `.env`
2. 配置必要的 API Keys:
   ```
   VITE_DASHSCOPE_API_KEY=your_key_here
   VITE_DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   VITE_DASHSCOPE_MODEL=qwen-vl-plus
   ```

### 启动开发服务器
```bash
npm install
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 📝 代码规范

### 导入顺序
1. React 相关
2. 第三方库
3. 类型定义
4. 服务
5. 常量和工具

### 命名规范
- **组件**: PascalCase (如 `PageProfile`)
- **函数**: camelCase (如 `calculateAge`)
- **常量**: UPPER_SNAKE_CASE (如 `MOCK_GAMES`)
- **类型**: PascalCase (如 `ChildProfile`)

### 文件组织
- 一个文件一个主要组件/功能
- 相关的辅助函数可以放在同一文件
- 类型定义统一在 `types/index.ts`

## 🔄 待优化项

### 短期优化
1. ✅ 文件结构重组（已完成）
2. ⏳ 组件拆分（App.tsx 过大）
3. ⏳ 状态管理优化（考虑 Context API）
4. ⏳ 错误处理完善

### 长期优化
1. ⏳ 单元测试
2. ⏳ E2E 测试
3. ⏳ 性能优化
4. ⏳ PWA 支持
5. ⏳ 国际化支持

## 📚 相关文档

- [源代码说明](./src/README.md)
- [API 文档](./services/README.md) (待创建)
- [组件文档](./components/README.md) (待创建)

## 🤝 贡献指南

1. 遵循现有代码风格
2. 添加必要的注释
3. 更新相关文档
4. 测试新功能

## 📄 许可证

本项目为私有项目，未经授权不得使用。
