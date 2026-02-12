# 🚀 快速启动 - 雷达图时间轴测试

## 一键启动测试

### 步骤 1：启动开发服务器

```bash
cd frontend
npm run dev
```

服务器将在 **http://localhost:3000** 启动

> 💡 如果 3000 端口被占用，Vite 会自动尝试其他端口（如 3001）

### 步骤 2：注入测试数据

打开浏览器，访问以下任一方式：

#### 方式 A：网页工具（推荐）

访问：**http://localhost:3000/seed-data.html**

点击"🚀 初始化所有测试数据"按钮

#### 方式 B：浏览器控制台

1. 访问：**http://localhost:3000**
2. 按 F12 打开开发者工具
3. 在控制台输入：
   ```javascript
   initTestData()
   ```

### 步骤 3：查看雷达图

1. 点击左上角菜单按钮（☰）
2. 选择"兴趣雷达图"
3. 拖动时间轴滑块或点击"播放"按钮

## 🎯 你会看到什么

- **30 天的数据演变**：从第 1 天到第 30 天
- **5 个发展阶段**：
  - 初期：视觉和触觉探索
  - 中期：建构和秩序建立
  - 后期：社交和运动增强
- **动态雷达图**：随时间轴变化的雷达图形状
- **实时摘要**：每个时间点的数据分析

## 🔧 故障排除

### 端口被占用

如果看到 "Port 3000 is in use"：
- Vite 会自动尝试 3001、3002 等端口
- 使用实际显示的端口号访问

### 数据没有显示

1. 打开控制台（F12）
2. 运行：`localStorage.getItem('asd_floortime_behaviors')`
3. 如果为 null，重新运行 `initTestData()`

### 清空数据重新开始

在控制台运行：
```javascript
clearData()
initTestData()
```

然后刷新页面。

## 📚 更多信息

- 详细使用指南：`TEST_DATA_GUIDE.md`
- 雷达图功能说明：`RADAR_CHART_FEATURE.md`
- 评估功能说明：`ASSESSMENT_FEATURES.md`
