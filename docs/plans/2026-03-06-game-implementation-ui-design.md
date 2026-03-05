# 游戏实施界面优化设计文档

**日期**: 2026-03-06
**设计师**: Claude + 用户协作
**状态**: 已批准

---

## 1. 需求概述

### 1.1 背景
当前游戏实施界面缺少快捷行为记录功能，家长需要手动记录孩子行为，操作不便。老师建议添加快捷按钮来记录常见行为（如"孩子微笑了"、"孩子不配合"等）。

### 1.2 目标
1. 添加6个快捷行为记录按钮，方便家长快速记录孩子行为
2. 优化游戏实施界面UI，采用温暖亲和风格
3. 实现单屏布局，避免滚动带来的操作困难
4. 记录的行为数据持久化，并在游戏复盘时提供给AI分析

---

## 2. 快捷按钮设计

### 2.1 行为类型（6个）

| 图标 | 名称 | 枚举值 | 颜色 |
|------|------|--------|------|
| 👁️ | 眼神接触 | `eye_contact` | 蓝色渐变 `from-blue-400 to-blue-500` |
| 🗣️ | 主动回应 | `active_response` | 绿色渐变 `from-green-400 to-green-500` |
| 😄 | 微笑开心 | `smile_happy` | 黄色渐变 `from-yellow-400 to-orange-400` |
| 🚫 | 拒绝抗拒 | `refuse_resistant` | 红色渐变 `from-red-400 to-red-500` |
| 📱 | 分心走神 | `distracted` | 紫色渐变 `from-purple-400 to-purple-500` |
| 🎯 | 专注投入 | `focused_engaged` | 青色渐变 `from-teal-400 to-teal-500` |

### 2.2 交互方式
- **点击即记录**：每次点击立即记录一条（带时间戳）
- **可重复点击**：同一按钮可多次点击
- **无状态管理**：不做选中状态，点击即完成
- **视觉反馈**：点击时按钮短暂闪烁（0.5秒），显示"✓ 已记录"

### 2.3 布局位置
固定在步骤导航按钮上方，作为底部固定栏的一部分。

---

## 3. 整体UI布局设计

### 3.1 设计风格
- **风格**：温暖亲和风
- **特点**：圆角、渐变色、插画元素
- **适用场景**：儿童干预场景，友好亲切

### 3.2 单屏布局结构（移动端）

```
┌─────────────────────────────────┐  ← 60px
│ 📸 积木游戏    ⏱️ 00:00  ✕退出  │     极简顶部栏
├─────────────────────────────────┤
│                                 │
│  📋 当前步骤说明               │  ← 50-60%高度
│  [可滚动]                       │     步骤说明区域
│                                 │     （最大空间）
│  这里是详细的步骤说明内容...    │
│                                 │
├─────────────────────────────────┤  ← 80px
│  👁️ 🗣️ 😄 🚫 📱 🎯             │     快捷按钮栏
│ 眼神  回应  开心  拒绝  分心  专注 │
├─────────────────────────────────┤  ← 60px
│  [← 上一步]    [下一步 →]       │     步骤导航按钮
├─────────────────────────────────┤  ← 84px（收起）
│  ══════                         │
│  ▲ AI助手                       │     AI助手面板（可拉起）
└─────────────────────────────────┘
```

### 3.3 元素优先级排序

1. **步骤导航按钮**（上一步/下一步）- 第1重要
2. **生成的图片** - 第2重要（可小一点）
3. **AI视频通话和游戏助手** - 第3重要（可拉起）
4. **当前步骤说明** - 第4重要（内容多，预留大空间）
5. **6个快捷按钮** - 第5重要
6. **计时器** - 第6重要

---

## 4. 详细组件设计

### 4.1 极简顶部栏（60px）

```
[📸 积木游戏] -------- [⏱️ 00:00] [✕ 退出]
     左                         中      右
```

- **左侧**：📸 游戏图标（20x20px）+ 游戏标题
- **中间**：计时器（蓝色圆圈，白色数字）
- **右侧**：✕ 退出互动按钮（红色文字）

### 4.2 步骤说明区域（50-60%高度）

- **布局**：占据屏幕最大空间
- **滚动**：内部可滚动，整体页面不滚动
- **对齐**：文字左对齐（不居中）
- **样式**：圆角卡片容器，柔和阴影

### 4.3 快捷按钮栏（80px）

```
┌─────────────────────────────────┐
│  👁️   🗣️   😄   🚫   📱   🎯     │
│ 眼神  回应  开心  拒绝  分心  专注 │
└─────────────────────────────────┘
```

- **容器**：80px高度，白色背景，顶部圆角
- **按钮尺寸**：50x50px 圆形按钮
- **排列**：6个按钮横向均匀分布
- **图标**：24x24px
- **文字**：10px，图标下方居中

### 4.4 步骤导航按钮（60px）

```
┌─────────────────────────────────┐
│    [← 上一步]    [下一步 →]     │
└─────────────────────────────────┘
```

- **上一步**：白色背景，灰色边框，深灰色文字
- **下一步/完成**：蓝绿渐变 `from-blue-500 to-green-500`，白色文字，阴影
- **最后一步**：显示"完成挑战"，绿色渐变
- **第一步时**：上一步按钮禁用（灰色半透明）

### 4.5 AI助手面板

#### 收起状态（84px）
```
┌─────────────────────────────────┐
│  ══════                         │  拖动把手
│  ▲ AI助手                       │
└─────────────────────────────────┘
```

- **拖动把手**：`w-12 h-1.5 bg-gray-200 rounded-full`
- **圆角**：`rounded-t-[32px]`
- **阴影**：`shadow-[0_-8px_30px_rgba(0,0,0,0.12)]`
- **可拖动**：向上拖动展开

#### 展开状态（50vh-90vh）

**游戏助手标签页（默认）**：
```
┌─────────────────────────────────┐
│  ══════                         │
│  ▼ [📹 AI视频通话] [💬 游戏助手]│
├─────────────────────────────────┤
│  👋 **你好！我是你的互动助手。** │
│     我已经准备好协助你...        │  聊天消息区域
│                                 │
│  [用户: 这个游戏怎么玩？]        │
│  [助手: 让我来解释...]          │
│                                 │
├─────────────────────────────────┤
│  [输入问题...] [发送→]          │  输入框（始终显示）
└─────────────────────────────────┘
```

**AI视频通话标签页**：
```
┌─────────────────────────────────┐
│  ══════                         │
│  ▼ [📹 AI视频通话] [💬 游戏助手]│
├─────────────────────────────────┤
│                                 │
│     ┌─────────────────────┐     │
│     │                     │     │
│     │   <video>           │     │  视频小窗口
│     │   摄像头预览         │     │
│     │                     │     │
│     └─────────────────────┘     │
│                                 │
│  ● AI观察中                     │  状态徽章
│                                 │
│  [📷] [🎤] [⛶] [✕]            │  控制按钮
│                                 │
└─────────────────────────────────┘
```

- **默认标签**：游戏助手
- **游戏助手**：聊天界面 + 底部输入框
- **AI视频通话**：视频小窗口 + 控制按钮（无输入框）
- **全屏功能**：点击⛶按钮后，使用现有的AIVideoCall组件全屏功能
- **标签切换**：选中蓝色背景，未选中灰色背景

---

## 5. 数据存储设计

### 5.1 数据库Schema

```typescript
export interface FloorGame {
  id: string;
  gameTitle: string;
  summary: string;
  goal: string;
  steps: GameStep[];
  materials?: string[];
  _analysis?: string;

  status: FloorGameStatus;
  dtstart: string;
  dtend: string;
  isVR: boolean;
  result?: string;
  evaluation?: EvaluationResult;
  chat_history_in_game?: string;
  review?: GameReviewResult;

  // 新增：游戏过程中的快捷按钮记录
  record_during_game?: QuickRecord[];
}

// 快捷记录接口
export interface QuickRecord {
  id: string;                    // 唯一标识
  timestamp: string;             // ISO 8601时间戳
  behaviorType: BehaviorType;    // 行为类型
  stepIndex: number;             // 当前步骤索引
}

// 行为类型枚举
export enum BehaviorType {
  EYE_CONTACT = 'eye_contact',           // 眼神接触 👁️
  ACTIVE_RESPONSE = 'active_response',   // 主动回应 🗣️
  SMILE_HAPPY = 'smile_happy',           // 微笑开心 😄
  REFUSE_RESISTANT = 'refuse_resistant', // 拒绝抗拒 🚫
  DISTRACTED = 'distracted',             // 分心走神 📱
  FOCUSED_ENGAGED = 'focused_engaged'    // 专注投入 🎯
}
```

### 5.2 数据格式示例

```json
{
  "id": "floor_game_123",
  "gameTitle": "积木搭建游戏",
  "status": "已完成",
  "dtstart": "2026-03-06T10:00:00Z",
  "dtend": "2026-03-06T10:15:00Z",
  "record_during_game": [
    {
      "id": "record-1",
      "timestamp": "2026-03-06T10:02:30Z",
      "behaviorType": "eye_contact",
      "stepIndex": 0
    },
    {
      "id": "record-2",
      "timestamp": "2026-03-06T10:05:15Z",
      "behaviorType": "smile_happy",
      "stepIndex": 1
    },
    {
      "id": "record-3",
      "timestamp": "2026-03-06T10:08:00Z",
      "behaviorType": "focused_engaged",
      "stepIndex": 2
    }
  ]
}
```

### 5.3 前端存储实现

```typescript
// 点击快捷按钮时记录
const handleQuickRecord = (behaviorType: BehaviorType) => {
  const record: QuickRecord = {
    id: `record-${Date.now()}-${Math.random()}`,
    timestamp: new Date().toISOString(),
    behaviorType: behaviorType,
    stepIndex: currentStepIndex
  };

  // 保存到当前游戏对象
  if (internalActiveGame) {
    if (!internalActiveGame.record_during_game) {
      internalActiveGame.record_during_game = [];
    }
    internalActiveGame.record_during_game.push(record);

    // 持久化到localStorage
    floorGameStorageService.updateGame(internalActiveGame);
  }

  // 显示记录反馈（短暂闪烁）
  showRecordFeedback(behaviorType);
};
```

### 5.4 游戏复盘Agent集成

```typescript
// 构造上下文时包含快捷按钮记录
const buildGameReviewContext = (
  floorGame: FloorGame,
  childProfile: ChildProfile
): string => {
  let context = `游戏名称：${floorGame.gameTitle}\n`;
  context += `儿童：${childProfile.name}\n`;
  context += `游戏时长：${calculateDuration(floorGame)}分钟\n\n`;

  // 添加快捷按钮记录
  if (floorGame.record_during_game && floorGame.record_during_game.length > 0) {
    context += `**游戏过程中的行为记录**：\n`;
    floorGame.record_during_game.forEach((record, idx) => {
      const behaviorLabel = getBehaviorLabel(record.behaviorType);
      const stepLabel = floorGame.steps[record.stepIndex]?.stepTitle || '未知步骤';
      const time = new Date(record.timestamp).toLocaleTimeString();
      context += `${idx + 1}. [${time}] ${behaviorLabel}（步骤：${stepLabel}）\n`;
    });
    context += '\n';
  }

  return context;
};
```

---

## 6. 实现要点

### 6.1 UI组件修改
1. 修改 `GameStepCard.tsx`，实现新的单屏布局
2. 添加快捷按钮栏组件
3. 调整AI助手面板，集成标签页切换功能
4. 文字左对齐，移除居中样式

### 6.2 数据流
1. 用户点击快捷按钮 → 记录行为（时间戳 + 步骤索引）
2. 保存到 `FloorGame.record_during_game` 数组
3. 持久化到 localStorage
4. 游戏结束时，将记录发送给游戏复盘Agent

### 6.3 动画效果
1. 使用 framer-motion 实现平滑动画
2. 快捷按钮点击闪烁效果（0.5秒）
3. AI助手面板展开/收起动画
4. 标签页切换动画

### 6.4 移动端适配
1. 主要针对移动端设计
2. 单屏布局，避免整体滚动
3. 步骤说明区域内部可滚动
4. 触摸友好的按钮尺寸（最小44x44px）

---

## 7. 技术栈

- **前端框架**：React 18 + TypeScript
- **动画库**：framer-motion
- **图标库**：lucide-react + emoji
- **样式方案**：Tailwind CSS
- **存储方案**：localStorage (floorGameStorageService)

---

## 8. 后续步骤

1. ✅ 设计方案已批准
2. ⏳ 调用 `writing-plans` 技能创建详细实现计划
3. ⏳ 实现 UI 组件修改
4. ⏳ 实现数据存储逻辑
5. ⏳ 集成游戏复盘Agent
6. ⏳ 测试和优化

---

**文档版本**: v1.0
**最后更新**: 2026-03-06
