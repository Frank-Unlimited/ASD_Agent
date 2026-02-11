# ASD 地板时光干预辅助系统 - 文档中心

## 📚 文档索引

### 快速开始
- [快速启动指南](2026-02-11-QUICK_START.md) - 一键启动和测试雷达图功能

### 核心功能文档

#### 1. 兴趣维度分析
- [关联度与强度分离功能](2026-02-11-INTENSITY_FEATURE.md) - 行为解析中的关联度和强度分离机制
- [兴趣维度雷达图](2026-02-11-RADAR_CHART_FEATURE.md) - 时间轴动态可视化功能

#### 2. 评估系统
- [综合评估功能](2026-02-11-ASSESSMENT_FEATURES.md) - AI 生成的综合评估报告

#### 3. 测试工具
- [测试数据注入指南](2026-02-11-TEST_DATA_GUIDE.md) - 生成测试数据的完整指南

## 🎯 系统架构概览

### 前端架构
```
frontend/
├── src/
│   ├── components/          # React 组件
│   │   └── RadarChartPage.tsx    # 雷达图页面
│   ├── services/            # 业务逻辑服务
│   │   ├── radarChartService.ts  # 雷达图数据服务
│   │   ├── behaviorStorage.ts    # 行为数据存储
│   │   ├── assessmentAgent.ts    # 评估 Agent
│   │   └── qwenService.ts        # LLM 服务
│   ├── types/               # TypeScript 类型定义
│   └── utils/               # 工具函数
│       └── seedTestData.ts       # 测试数据生成
├── docs/                    # 文档目录
└── seed-data.html          # 测试数据注入工具
```

### 数据流
```
用户输入 → LLM 分析 → 行为记录 → localStorage → 雷达图可视化
                ↓
            评估报告
```

## 🔄 最近更新（2026-02-11）

### 重大重构

#### 1. 兴趣维度分析系统升级
- ✅ 分离关联度（weight）和强度（intensity）
- ✅ 关联度：0.1-1.0，表示行为与维度的关联程度
- ✅ 强度：-1.0 到 1.0，表示喜欢/讨厌程度
- ✅ 优化 LLM 提示词和 Schema 定义

#### 2. 雷达图时间轴功能
- ✅ 从静态时间范围选择改为动态时间轴
- ✅ 添加拖动条交互
- ✅ 实现自动播放功能
- ✅ 累计数据计算
- ✅ 平滑动画过渡

#### 3. 评估系统简化
- ✅ 从 7 个字段简化为 3 个核心字段
- ✅ 统一报告类型（Report）
- ✅ 支持 AI 生成的评估报告

#### 4. 测试工具完善
- ✅ 创建测试数据生成脚本
- ✅ 提供网页工具界面
- ✅ 生成 30 天跨度的测试数据
- ✅ 模拟真实的兴趣发展过程

## 📊 核心数据模型

### 行为分析（BehaviorAnalysis）
```typescript
{
  id: string;
  behavior: string;              // 行为描述
  matches: InterestMatch[];      // 兴趣维度匹配
  timestamp: string;             // 记录时间
  source: 'GAME' | 'REPORT' | 'CHAT';
}
```

### 兴趣匹配（InterestMatch）
```typescript
{
  dimension: InterestDimensionType;  // 维度类型
  weight: number;                    // 关联度 0.1-1.0
  intensity: number;                 // 强度 -1.0 到 1.0
  reasoning: string;                 // 推理说明
}
```

### 8 个兴趣维度
- Visual（视觉）
- Auditory（听觉）
- Tactile（触觉）
- Motor（运动）
- Construction（建构）
- Order（秩序）
- Cognitive（认知）
- Social（社交）

## 🛠️ 开发指南

### 环境要求
- Node.js 16+
- npm 或 yarn
- 现代浏览器（支持 ES6+）

### 启动开发服务器
```bash
cd frontend
npm install
npm run dev
```

### 注入测试数据
访问 http://localhost:3000/seed-data.html

### 构建生产版本
```bash
npm run build
```

## 🔗 相关资源

### 外部依赖
- React 19 - UI 框架
- Recharts - 图表库
- Tailwind CSS - 样式框架
- Lucide React - 图标库

### API 服务
- 通义千问 API - LLM 服务
- localStorage - 数据持久化

## 📝 贡献指南

### 添加新功能
1. 在 `src/types/index.ts` 中定义类型
2. 在 `src/services/` 中实现业务逻辑
3. 在 `src/components/` 中创建 UI 组件
4. 更新相关文档

### 文档规范
- 文件名格式：`YYYY-MM-DD-FEATURE_NAME.md`
- 使用中文编写
- 包含代码示例和使用说明
- 更新 README.md 索引

## 🐛 问题反馈

如遇到问题，请检查：
1. 浏览器控制台错误信息
2. localStorage 数据是否正确
3. API 密钥是否配置
4. 网络连接是否正常

## 📅 更新日志

### 2026-02-11
- 重构兴趣维度分析系统
- 实现雷达图时间轴功能
- 简化评估系统
- 完善测试工具
- 整理项目文档

---

最后更新：2026-02-11
