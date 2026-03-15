# 行为与兴趣页面整合设计文档

**日期**: 2026-03-07
**设计师**: Claude Sonnet 4.6
**状态**: ✅ 已批准

---

## 概述

将现有的"行为数据"页面和"兴趣雷达图"页面整合为一个统一的"行为与兴趣"页面，提供更紧凑的用户体验和更好的信息关联���。

### 目标

- 整合两个独立页面为一个统一视图
- 保留所有原有功能和交互特性
- 优化视觉布局，提升用户体验
- 简化导航结构

---

## 用户需求

### 功能要求

1. **保留全部功能**
   - 雷达图的所有功能（时间轴、播放控制、图表类型切换）
   - 行为数据的所有功能（筛选、搜索、详情查看）

2. **布局比例**
   - 雷达图部分：约占页面 40-50%
   - 行为数据部分：约占页面 50-60%

3. **数据独立性**
   - 雷达图的时间轴筛选不影响行为数据列表
   - 行为数据始终显示所有记录

4. **滚动体验**
   - 采用整体滚动方式
   - 雷达图和行为数据在同一滚动容器中

5. **命名统一**
   - 新页面名称："行为与兴趣"
   - 合并原有菜单项

---

## 设计方案

### 整体布局结构

```
┌──────────────────────────────────────────┐
│  🎯 行为与兴趣分析                         │  ← 统一标题栏
├──────────────────────────────────────────┤
│                                          │
│  【雷达图部分 - 约45%】                    │
│  ┌──────────────────────────────────┐  │
│  │ 图表类型切换（关联度/强度/两者）      │  │
│  ├──────────────────────────────────┤  │
│  │ 时间轴控制器                        │  │
│  │ - 日期显示 & 数据摘要               │  │
│  │ - 时间轴��块                       │  │
│  │ - 播放/暂停/重置按钮               │  │
│  ├──────────────────────────────────┤  │
│  │ 雷达图可视化                       │  │
│  ├──────────────────────────────────┤  │
│  │ 使用说明                           │  │
│  └──────────────────────────────────┘  │
│                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │  ← 浅色分隔线
│                                          │
│  【行为数据部分 - 约55%】                  │
│  ┌──────────────────────────────────┐  │
│  │ 统计卡片（3个数据指标）              │  │
│  ├──────────────────────────────────┤  │
│  │ 筛选器                             │  │
│  │ - 兴趣维度筛选                     │  │
│  │ - 数据来源筛选                     │  │
│  ├──────────────────────────────────┤  │
│  │ 行为记录列表（可滚动）               │  │
│  └──────────────────────────────────┘  │
│                                          │
└──────────────────────────────────────────┘
```

### 第一部分：统一标题栏

```tsx
<div className="mb-4 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-5 text-white shadow-lg">
  <h2 className="text-xl font-bold flex items-center">
    <TrendingUp className="w-6 h-6 mr-2" />
    行为与兴趣分析
  </h2>
  <p className="text-sm text-indigo-100 mt-1">
    查看兴趣维度演变和行为记录数据
  </p>
</div>
```

### 第二部分：雷达图区域（约45%高度）

#### 组件结构

1. **图表类型切换器**
   - 三个按钮：关联度、强度、两者
   - 渐变背景：`from-white to-indigo-50`
   - 边框：`border-2 border-indigo-100`

2. **时间轴控制器**
   - 当前日期和数据摘要显示
   - 时间轴滑块（可拖动）
   - 播放控制按钮：重置、播放/暂停
   - 渐变背景：`from-white to-purple-50`

3. **雷达图可视化**
   - 使用 Recharts 库的 `RadarChart`
   - 响应式容器，高度 400px
   - 支持多条雷达线（关联度/强度）
   - 自定义 Tooltip 显示详细信息

4. **使用说明**
   - 灰色背景卡片
   - 列表形式展示使用指南

#### 保持的功能

- ✅ 图表类型切换（关联度/强度/两者）
- ✅ 时间轴滑块拖动
- ✅ 播放/暂停/重置控制
- ✅ 自动播放功能（每秒前进一步）
- ✅ 自定义 Tooltip
- ✅ 数据摘要显示
- ✅ 使用说明

### 第三部分：行为数据区域（约55%高度）

#### 组件结构

1. **统计卡片**
   - 紫色渐变背景：`from-purple-500 to-indigo-600`
   - 三个统计指标：总记录数、游戏记录、报告记录
   - 半透明白色背景的数据卡片

2. **筛选器**
   - 兴趣维度筛选：9个维度 + 全部
   - 数据来源筛选：游戏/报告/对话 + 全部
   - 白色背景，带阴影

3. **行为记录列表**
   - 卡片式布局，每条记录一个卡片
   - 显示：行为描述、兴趣标签、来源图标、日期
   - 点击查看详情弹窗
   - 支持删除单条记录
   - 支持清空全部记录

#### 保持的功能

- ✅ 三个统计指标卡片
- ✅ 按兴趣维度筛选（9个维度）
- ✅ 按数据来源筛选（游戏/报告/对话）
- ✅ 行为记录列表展示
- ✅ 点击查看详情弹窗
- ✅ 删除单条记录
- ✅ 清空全部记录

### 第四部分：分隔线

```tsx
<div className="border-t border-gray-200 my-4" />
```

使用浅色分隔线，不要过于明显，保持页面视觉流畅性。

---

## 技术实现

### 文件结构

```
frontend/src/
├── components/
│   ├── BehaviorAndInterestPage.tsx    ← 新建：整合后的页面组件
│   ├── RadarChartPage.tsx             ← 保留：代码参考
│   └── ...
├── App.tsx                            ← 修改：更新导航和页面路由
└── ...
```

### 组件设计

```typescript
// BehaviorAndInterestPage.tsx
interface BehaviorAndInterestPageProps {
  childProfile: ChildProfile | null;
}

const BehaviorAndInterestPage: React.FC<BehaviorAndInterestPageProps> = ({
  childProfile
}) => {
  // ===== 雷达图相关状态 =====
  const [chartType, setChartType] = useState<RadarChartType>('both');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // ===== 行为数据相关状态 =====
  const [behaviors, setBehaviors] = useState<BehaviorAnalysis[]>([]);
  const [filterDimension, setFilterDimension] = useState<string>('全部');
  const [filterSource, setFilterSource] = useState<string>('全部');
  const [stats, setStats] = useState<any>(null);
  const [selectedBehavior, setSelectedBehavior] = useState<BehaviorAnalysis | null>(null);

  // ===== 数据获取 =====
  const timelineData = useMemo(() => getTimelineData(), []);

  useEffect(() => {
    loadBehaviors();
  }, [filterDimension, filterSource]);

  // ===== 事件处理 =====
  const loadBehaviors = () => {
    // 从 behaviorStorageService 加载数据
  };

  const handleDeleteBehavior = (id: string) => {
    // 删除逻辑
  };

  // ===== 渲染 =====
  return (
    <div className="h-full overflow-y-auto bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4 pb-20">
      {/* 统一标题 */}
      <PageHeader />

      {/* 浅色分隔线 */}
      <div className="border-t border-gray-200 my-4" />

      {/* 雷达图部分 */}
      <RadarChartSection
        chartType={chartType}
        setChartType={setChartType}
        currentIndex={currentIndex}
        setCurrentIndex={setCurrentIndex}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
        timelineData={timelineData}
      />

      {/* 浅色分隔线 */}
      <div className="border-t border-gray-200 my-4" />

      {/* 行为数据部分 */}
      <BehaviorDataSection
        behaviors={behaviors}
        filterDimension={filterDimension}
        setFilterDimension={setFilterDimension}
        filterSource={filterSource}
        setFilterSource={setFilterSource}
        stats={stats}
        selectedBehavior={selectedBehavior}
        setSelectedBehavior={setSelectedBehavior}
        onDeleteBehavior={handleDeleteBehavior}
        loadBehaviors={loadBehaviors}
      />

      {/* 详情弹窗 */}
      {selectedBehavior && (
        <BehaviorDetailModal
          behavior={selectedBehavior}
          onClose={() => setSelectedBehavior(null)}
        />
      )}
    </div>
  );
};
```

### 子组件拆分

为了代码可维护性，建议将页面拆分为以下子组件：

1. **RadarChartSection**
   - 包含雷达图相关的所有UI元素
   - 管理雷达图的状态和交互

2. **BehaviorDataSection**
   - 包含行为数据相关的所有UI元素
   - 管理筛选和数据展示逻辑

3. **BehaviorDetailModal**
   - 行为详情弹窗组件
   - 复用现有的弹窗设计

### App.tsx 修改

```typescript
// 修改前
{currentPage === Page.BEHAVIORS && <PageBehaviors childProfile={childProfile} />}
{currentPage === Page.RADAR && <PageRadar />}

// 修改后
{currentPage === Page.BEHAVIORS && <BehaviorAndInterestPage childProfile={childProfile} />}
{currentPage === Page.RADAR && <BehaviorAndInterestPage childProfile={childProfile} />}
```

### 导航菜单修改

```typescript
// 修改前
<button onClick={() => { setPage(Page.BEHAVIORS); onClose(); }}>
  <Activity className="w-5 h-5 text-primary" />
  <span>行为数据</span>
</button>
<button onClick={() => { setPage(Page.RADAR); onClose(); }}>
  <TrendingUp className="w-5 h-5 text-primary" />
  <span>兴趣雷达图</span>
</button>

// 修改后
<button onClick={() => { setPage(Page.BEHAVIORS); onClose(); }}>
  <TrendingUp className="w-5 h-5 text-primary" />
  <span>行为与兴趣</span>
</button>
```

### 依赖项

保持现有的依赖项不变：

- `recharts` - 雷达图可视化
- `lucide-react` - 图标库
- `framer-motion` - 动画（如需要）

---

## 视觉设计规范

### 颜色方案

| 用途 | 颜色 | CSS 类 |
|------|------|--------|
| 标题渐变 | 紫色到靛蓝 | `from-indigo-500 to-purple-600` |
| 雷达图背景 | 白色到靛蓝 | `from-white to-indigo-50` |
| 时间轴背景 | 白色到紫色 | `from-white to-purple-50` |
| 统计卡片背景 | 紫色到靛蓝 | `from-purple-500 to-indigo-600` |
| 页面背景 | 靛蓝到白色到紫色 | `from-indigo-50 via-white to-purple-50` |
| 分隔线 | 浅灰 | `border-gray-200` |

### 间距规范

- 页面内边距：`p-4`
- 卡片内边距：`p-4` 或 `p-5`
- 卡片间距：`mb-4` 或 `space-y-4`
- 分隔线边距：`my-4`

### 圆角规范

- 大卡片：`rounded-2xl`
- 小卡片/按钮：`rounded-xl` 或 `rounded-lg`

### 阴影规范

- 标题卡片：`shadow-lg`
- 普通卡片：`shadow-sm` 或 `shadow-lg`

---

## 数据流设计

### 雷达图数据流

```
getTimelineData() (从 radarChartService)
  ↓
timelineData (时间轴数据数组)
  ↓
currentIndex (当前选中时间点)
  ↓
currentData (当前时间点数据)
  ↓
chartData (转换为 Recharts 格式)
  ↓
RadarChart 渲染
```

### 行为数据流

```
behaviorStorageService.getAllBehaviors()
  ↓
应用筛选条件 (filterDimension, filterSource)
  ↓
behaviors (筛选后的行为列表)
  ↓
BehaviorDataSection 渲染
```

### 状态管理

所有状态都在 `BehaviorAndInterestPage` 组件中管理，不需要额外的状态管理库。

---

## 用户体验设计

### 滚动行为

1. **整体滚动**
   - 所有内容在一个滚动容器中
   - 用户可以自然地向下滚动查看行为数据

2. **滚动位置记忆**
   - 可选：使用 `localStorage` 记住用户的滚动位置
   - 返回页面时恢复到上次浏览的位置

### 交互反馈

1. **按钮点击**
   - 使用 `transform hover:scale-105` 提供缩放反馈
   - 使用 `transition-all` 平滑过渡

2. **加载状态**
   - 数据加载时显示加载指示器
   - 空状态时显示友好的提示信息

3. **错误处理**
   - 删除操作需要二次确认
   - 清空全部需要确认对话框

### 响应式设计

- 移动端：保持堆叠布局，适当调整间距
- 平板端：可以利用横向空间展示更多信息
- 桌面端：可以考虑固定宽度容器，居中显示

---

## 测试计划

### 功能测试

1. **雷达图功能**
   - [ ] 图表类型切换正常
   - [ ] 时间轴滑块拖动流畅
   - [ ] 播放/暂停/重置按钮工作正常
   - [ ] Tooltip 正确显示数据

2. **行为数据功能**
   - [ ] 筛选器工作正常
   - [ ] 行为列表正确显示
   - [ ] 详情弹窗正确打开
   - [ ] 删除功能正常工作
   - [ ] 清空全部功能正常工作

3. **整合功能**
   - [ ] 页面滚动流畅
   - [ ] 雷达图不影响行为数据显示
   - [ ] 菜单导航正确跳转

### 兼容性测试

- [ ] Chrome 最新版
- [ ] Firefox 最新版
- [ ] Safari 最新版
- [ ] 移动端浏览器（iOS Safari、Chrome Mobile）

### 性能测试

- [ ] 页面加载时间 < 2秒
- [ ] 滚动帧率 > 60fps
- [ ] 时间轴切换响应时间 < 100ms

---

## 实施计划

详细的实施计划将在下一步使用 `writing-plans` skill 创建。

### 预估工作量

- 创建新组件：2-3小时
- 整合现有代码：1-2小时
- 测试和调试：1-2小时
- 文档更新：0.5-1小时

**总计**：约 5-8 小时

### 风险评估

- **低风险**：主要是代码整合，不涉及复杂逻辑
- **兼容性**：保持现有依赖，风险低
- **性能**：页面变长，但滚动性能应该可以接受

---

## 后续优化建议

1. **性能优化**
   - 考虑使用虚拟滚动优化长列表
   - 懒加载雷达图组件

2. **功能增强**
   - 添加数据导出功能
   - 添加自定义时间范围筛选
   - 添加行为数据与雷达图的联动筛选（可选）

3. **UI/UX 改进**
   - 添加页面内快速导航（锚点跳转）
   - 优化移动端体验
   - 添加暗色模式支持

---

## 附录

### 相关文件

- `frontend/src/components/RadarChartPage.tsx` - 原雷达图页面
- `frontend/src/App.tsx` - 行为数据页面（PageBehaviors 组件）
- `frontend/src/services/radarChartService.ts` - 雷达图数据服务
- `frontend/src/services/behaviorStorage.ts` - 行为数据存储服务

### 参考文档

- Recharts 文档：https://recharts.org/
- Tailwind CSS 文档：https://tailwindcss.com/
- Lucide Icons：https://lucide.dev/

---

**文档版本**: 1.0
**最后更新**: 2026-03-07
**状态**: ✅ 已批准，等待实施
