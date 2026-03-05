# 游戏实施界面优化实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 优化游戏实施界面，添加6个快捷行为记录按钮，实现单屏布局和温暖亲和风格设计

**Architecture:**
- 修改 GameStepCard 组件，实现新的单屏布局（极简顶部栏 + 步骤说明区域 + 快捷按钮栏 + 步骤导航 + AI助手面板）
- 添加快捷按钮记录功能，数据持久化到 FloorGame.record_during_game
- 集成游戏复盘Agent，将行为记录作为上下文输入

**Tech Stack:** React 18, TypeScript, Tailwind CSS, framer-motion, lucide-react

---

## Task 1: 更新类型定义

**Files:**
- Modify: `frontend/src/types/index.ts`

**Step 1: 添加新的类型定义**

在 `frontend/src/types/index.ts` 文件末尾添加：

```typescript
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

**Step 2: 修改 FloorGame 接口**

在 `FloorGame` 接口中添加新字段：

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
```

**Step 3: 提交更改**

```bash
git add frontend/src/types/index.ts
git commit -m "feat(types): 添加快捷记录类型定义

- 添加 QuickRecord 接口
- 添加 BehaviorType 枚举（6种行为类型）
- 在 FloorGame 接口中添加 record_during_game 字段"
```

---

## Task 2: 创建快捷按钮栏组件

**Files:**
- Create: `frontend/src/components/QuickRecordBar.tsx`

**Step 1: 创建快捷按钮栏组件**

```typescript
import React, { useState } from 'react';
import { BehaviorType } from '../types';

interface QuickRecordBarProps {
  onRecord: (behaviorType: BehaviorType) => void;
}

const BEHAVIORS = [
  { type: BehaviorType.EYE_CONTACT, icon: '👁️', label: '眼神', color: 'from-blue-400 to-blue-500' },
  { type: BehaviorType.ACTIVE_RESPONSE, icon: '🗣️', label: '回应', color: 'from-green-400 to-green-500' },
  { type: BehaviorType.SMILE_HAPPY, icon: '😄', label: '开心', color: 'from-yellow-400 to-orange-400' },
  { type: BehaviorType.REFUSE_RESISTANT, icon: '🚫', label: '拒绝', color: 'from-red-400 to-red-500' },
  { type: BehaviorType.DISTRACTED, icon: '📱', label: '分心', color: 'from-purple-400 to-purple-500' },
  { type: BehaviorType.FOCUSED_ENGAGED, icon: '🎯', label: '专注', color: 'from-teal-400 to-teal-500' },
];

export const QuickRecordBar: React.FC<QuickRecordBarProps> = ({ onRecord }) => {
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleClick = (behaviorType: BehaviorType, label: string) => {
    onRecord(behaviorType);

    // 显示反馈
    setFeedback(`✓ 已记录：${label}`);
    setTimeout(() => setFeedback(null), 800);
  };

  return (
    <div className="flex flex-col items-center bg-white rounded-t-3xl shadow-md border-b border-gray-100 py-3 px-2">
      {/* 反馈提示 */}
      {feedback && (
        <div className="text-xs font-bold text-green-600 mb-2 animate-pulse">
          {feedback}
        </div>
      )}

      {/* 按钮组 */}
      <div className="flex justify-around items-center w-full max-w-lg">
        {BEHAVIORS.map((behavior) => (
          <button
            key={behavior.type}
            className={`flex flex-col items-center bg-gradient-to-br ${behavior.color} w-12 h-12 rounded-full shadow-md active:scale-90 transition-transform hover:shadow-lg`}
            onClick={() => handleClick(behavior.type, behavior.label)}
            title={behavior.label}
          >
            <span className="text-2xl">{behavior.icon}</span>
            <span className="text-[10px] text-white font-bold mt-0.5">{behavior.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
```

**Step 2: 提交组件**

```bash
git add frontend/src/components/QuickRecordBar.tsx
git commit -m "feat(component): 创建快捷按钮栏组件

- 添加6个快捷行为记录按钮
- 每个按钮带图标、标签和渐变色
- 点击时显示短暂反馈动画
- 使用 onRecord 回调通知父组件"
```

---

## Task 3: 重构 GameStepCard 组件

**Files:**
- Modify: `frontend/src/components/GameStepCard.tsx`

**Step 1: 重写 GameStepCard 组件**

完全重写 `frontend/src/components/GameStepCard.tsx`：

```typescript
import React, { useState } from 'react';
import { Timer, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { Game, FloorGame, BehaviorType } from '../types';
import { QuickRecordBar } from './QuickRecordBar';

interface GameStepCardProps {
  game: Game | FloorGame;
  currentStepIndex: number;
  timer: number;
  stepImages: Map<number, string>;
  onStepChange: (index: number) => void;
  onComplete: () => void;
  onAbort: () => void;
  onRecord: (behaviorType: BehaviorType) => void;
  formatTime: (seconds: number) => string;
}

export const GameStepCard: React.FC<GameStepCardProps> = ({
  game,
  currentStepIndex,
  timer,
  stepImages,
  onStepChange,
  onComplete,
  onAbort,
  onRecord,
  formatTime
}) => {
  const steps = 'steps' in game ? game.steps : [];
  const currentStep = steps[currentStepIndex];
  const isLastStep = currentStepIndex === steps.length - 1;

  const stepTitle = currentStep && 'stepTitle' in currentStep ? currentStep.stepTitle : `步骤 ${currentStepIndex + 1}`;
  const instruction = currentStep && 'instruction' in currentStep ? currentStep.instruction : '';
  const guidance = currentStep && 'guidance' in currentStep ? currentStep.guidance : '';

  return (
    <div className="flex flex-col h-full bg-white overflow-hidden">
      {/* 极简顶部栏 */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50/50 border-b border-gray-100 shrink-0 h-[60px]">
        {/* 左侧：图标 + 标题 */}
        <div className="flex items-center space-x-2 flex-1">
          {stepImages.get(currentStepIndex) && (
            <img
              src={stepImages.get(currentStepIndex)}
              alt="游戏图标"
              className="w-5 h-5 rounded-lg object-cover"
            />
          )}
          <span className="text-sm font-bold text-gray-800 truncate">{game.title || game.gameTitle}</span>
        </div>

        {/* 中间：计时器 */}
        <div className="flex items-center justify-center px-4">
          <div className="flex items-center text-blue-600 font-mono font-bold text-sm bg-blue-50 px-3 py-1 rounded-full">
            <Timer className="w-3 h-3 mr-1" />
            {formatTime(timer)}
          </div>
        </div>

        {/* 右侧：退出按钮 */}
        <button
          onClick={onAbort}
          className="text-red-500 font-bold text-xs hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors flex items-center border border-red-100"
        >
          <X className="w-3 h-3 mr-1" />
          退出
        </button>
      </div>

      {/* 步骤说明区域（可滚动） */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {/* 步骤标题 */}
        <div className="mb-3">
          <span className="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
            {stepTitle}
          </span>
        </div>

        {/* 步骤说明 */}
        <h2 className="text-lg font-bold text-gray-800 text-left mb-4 leading-relaxed">
          {instruction}
        </h2>

        {/* 互动建议 */}
        {guidance && (
          <div className="bg-blue-50/80 p-4 rounded-2xl border border-blue-100 mb-4">
            <p className="text-sm text-blue-900/80 leading-relaxed">
              <span className="font-bold">💡 互动建议：</span>
              {guidance}
            </p>
          </div>
        )}

        {/* 步骤图片（如果有且不是小图标） */}
        {stepImages.get(currentStepIndex) && (
          <div className="w-full rounded-2xl overflow-hidden shadow-md ring-4 ring-white mb-4">
            <img
              src={stepImages.get(currentStepIndex)}
              alt="步骤插图"
              className="w-full h-auto object-cover"
            />
          </div>
        )}
      </div>

      {/* 快捷按钮栏 */}
      <QuickRecordBar onRecord={onRecord} />

      {/* 步骤导航按钮 */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50/50 border-t border-gray-100 shrink-0 h-[60px]">
        <button
          onClick={() => onStepChange(Math.max(0, currentStepIndex - 1))}
          disabled={currentStepIndex === 0}
          className={`flex items-center text-gray-600 font-bold transition px-6 py-2.5 rounded-full border-2 border-gray-200 bg-white hover:bg-gray-50 active:scale-95 ${currentStepIndex === 0 ? 'opacity-30 cursor-not-allowed' : ''}`}
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          上一步
        </button>

        {isLastStep ? (
          <button
            onClick={onComplete}
            className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-8 py-2.5 rounded-full font-bold shadow-lg shadow-green-500/30 flex items-center hover:shadow-xl transition transform active:scale-95"
          >
            ✓ 完成挑战
          </button>
        ) : (
          <button
            onClick={() => onStepChange(currentStepIndex + 1)}
            className="bg-gradient-to-r from-blue-500 to-green-500 text-white px-8 py-2.5 rounded-full font-bold shadow-lg shadow-blue-500/30 flex items-center hover:shadow-xl transition transform active:scale-95"
          >
            下一步
            <ChevronRight className="w-4 h-4 ml-1" />
          </button>
        )}
      </div>
    </div>
  );
};
```

**Step 2: 提交更改**

```bash
git add frontend/src/components/GameStepCard.tsx
git commit -m "refactor(component): 重构GameStepCard组件

- 实现新的单屏布局（极简顶部栏 + 步骤说明 + 快捷按钮 + 导航）
- 文字左对齐，移除居中样式
- 添加 onRecord 回调支持快捷按钮记录
- 步骤说明区域可内部滚动
- 温暖亲和风格设计（圆角、渐变色）"
```

---

## Task 4: 更新 App.tsx 集成快捷按钮功能

**Files:**
- Modify: `frontend/src/App.tsx`

**Step 1: 找到 GameStepCard 的使用位置**

在 `frontend/src/App.tsx` 中搜索 `<GameStepCard` 的使用位置，约在第3769行。

**Step 2: 添加快捷按钮处理函数**

在 GameStepCard 使用位置附近添加处理函数：

```typescript
// 快捷按钮记录处理函数
const handleQuickRecord = (behaviorType: BehaviorType) => {
  if (!internalActiveGame) return;

  const record: QuickRecord = {
    id: `record-${Date.now()}-${Math.random()}`,
    timestamp: new Date().toISOString(),
    behaviorType: behaviorType,
    stepIndex: currentStepIndex
  };

  // 保存到当前游戏对象
  if (!internalActiveGame.record_during_game) {
    internalActiveGame.record_during_game = [];
  }
  internalActiveGame.record_during_game.push(record);

  // 持久化到localStorage
  floorGameStorageService.updateGame(internalActiveGame);

  console.log('✓ 已记录行为:', behaviorType, 'at step', currentStepIndex);
};
```

**Step 3: 更新 GameStepCard 调用**

找到 `<GameStepCard` 组件的调用，添加 `onRecord` 属性：

```typescript
<GameStepCard
  game={internalActiveGame}
  currentStepIndex={currentStepIndex}
  timer={timer}
  stepImages={stepImages}
  onStepChange={setCurrentStepIndex}
  onComplete={() => setGameState(GameState.FEEDBACK)}
  onAbort={() => onAbort && onAbort()}
  formatTime={formatTime}
  onRecord={handleQuickRecord}  // ← 新增
/>
```

**Step 4: 提交更改**

```bash
git add frontend/src/App.tsx
git commit -m "feat(integration): 集成快捷按钮记录功能

- 添加 handleQuickRecord 函数处理快捷按钮点击
- 将记录保存到 FloorGame.record_during_game
- 持久化到 localStorage
- 更新 GameStepCard 调用，传递 onRecord 回调"
```

---

## Task 5: 更新游戏复盘Agent集成

**Files:**
- Modify: `frontend/src/services/gameReviewAgent.ts` 或相关游戏复盘服务文件

**Step 1: 找到游戏复盘上下文构造函数**

搜索 `buildGameReviewContext` 或类似函数，该函数构造游戏复盘的上下文信息。

**Step 2: 添加行为记录到上下文**

在游戏复盘上下文中添加 `record_during_game` 数据：

```typescript
// 在构造上下文的函数中添加
if (floorGame.record_during_game && floorGame.record_during_game.length > 0) {
  context += `\\n**游戏过程中的行为记录**：\\n`;
  floorGame.record_during_game.forEach((record, idx) => {
    const behaviorLabel = getBehaviorLabel(record.behaviorType);
    const stepLabel = floorGame.steps[record.stepIndex]?.stepTitle || '未知步骤';
    const time = new Date(record.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    context += `${idx + 1}. [${time}] ${behaviorLabel}（步骤：${stepLabel}）\\n`;
  });
  context += '\\n';
}

// 辅助函数：获取行为标签
function getBehaviorLabel(behaviorType: BehaviorType): string {
  const labels = {
    [BehaviorType.EYE_CONTACT]: '眼神接触 👁️',
    [BehaviorType.ACTIVE_RESPONSE]: '主动回应 🗣️',
    [BehaviorType.SMILE_HAPPY]: '微笑开心 😄',
    [BehaviorType.REFUSE_RESISTANT]: '拒绝抗拒 🚫',
    [BehaviorType.DISTRACTED]: '分心走神 📱',
    [BehaviorType.FOCUSED_ENGAGED]: '专注投入 🎯'
  };
  return labels[behaviorType] || behaviorType;
}
```

**Step 3: 提交更改**

```bash
git add frontend/src/services/gameReviewAgent.ts
git commit -m "feat(agent): 集成快捷按钮记录到游戏复盘

- 将 record_during_game 数据添加到复盘上下文
- 显示时间戳、行为类型和对应步骤
- 帮助AI分析孩子在游戏过程中的行为表现"
```

---

## Task 6: 更新 AI 助手面板（可选优化）

**Files:**
- Modify: `frontend/src/components/AIAssistantPanel.tsx`

**Step 1: 确认标签页切换功能**

确保 `AIAssistantPanel` 组件已经支持标签页切换（游戏助手 / AI视频通话）。如果需要，可以参考现有实现。

**Step 2: 确保默认显示游戏助手标签**

如果需要修改，确保默认状态是游戏助手标签页。

**Step 3: 提交更改**

```bash
git add frontend/src/components/AIAssistantPanel.tsx
git commit -m "refactor(panel): 确保AI助手面板默认显示游戏助手标签

- 验证标签页切换功能正常
- 确保默认显示游戏助手（输入框可见）
- AI视频通话标签页无输入框"
```

---

## Task 7: 测试和验证

**Step 1: 启动开发服务器**

```bash
cd frontend
npm run dev
```

**Step 2: 手动测试清单**

1. ✅ 打开游戏实施界面，验证单屏布局是否正常显示
2. ✅ 验证极简顶部栏（图标 + 标题 + 计时器 + 退出按钮）
3. ✅ 验证步骤说明区域文字左对齐
4. ✅ 验证6个快捷按钮显示正确（图标、颜色、标签）
5. ✅ 点击快捷按钮，验证记录功能（检查控制台日志）
6. ✅ 验证按钮点击反馈动画（"✓ 已记录"提示）
7. ✅ 完成游戏后，验证数据是否保存到 localStorage
8. ✅ 验证游戏复盘是否包含行为记录数据

**Step 3: 测试数据持久化**

在浏览器控制台运行：

```javascript
// 检查 localStorage 中的游戏数据
const games = JSON.parse(localStorage.getItem('floorGames') || '[]');
const latestGame = games[games.length - 1];
console.log('最新游戏数据:', latestGame);
console.log('行为记录:', latestGame.record_during_game);
```

**Step 4: 提交测试结果**

```bash
# 如果测试通过，标记任务完成
echo "✅ 所有测试通过"
```

---

## Task 8: 文档更新（可选）

**Files:**
- Modify: `frontend/README.md` 或 `PROJECT_STRUCTURE.md`

**Step 1: 更新组件文档**

在相关文档中添加新组件的说明：

```markdown
### QuickRecordBar

快捷行为记录按钮栏组件。

**Props:**
- `onRecord: (behaviorType: BehaviorType) => void` - 点击按钮时的回调

**行为类型:**
- `eye_contact` - 眼神接触 👁️
- `active_response` - 主动回应 🗣️
- `smile_happy` - 微笑开心 😄
- `refuse_resistant` - 拒绝抗拒 🚫
- `distracted` - 分心走神 📱
- `focused_engaged` - 专注投入 🎯
```

**Step 2: 提交文档**

```bash
git add frontend/README.md
git commit -m "docs: 添加快捷按钮栏组件文档"
```

---

## 完成检查清单

- [ ] 类型定义已添加（QuickRecord, BehaviorType）
- [ ] FloorGame 接口已更新（record_during_game 字段）
- [ ] QuickRecordBar 组件已创建
- [ ] GameStepCard 组件已重构（新UI布局）
- [ ] App.tsx 已集成快捷按钮功能
- [ ] 游戏复盘Agent已集成行为记录
- [ ] 手动测试通过
- [ ] 数据持久化验证通过
- [ ] 文档已更新

---

**实施计划版本**: v1.0
**创建日期**: 2026-03-06
**预计时间**: 2-3小时

## 快速开始

按照任务顺序依次执行即可。每个任务都有明确的步骤和提交命令，确保代码质量和版本控制。
