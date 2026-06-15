# 综合评估系统重新设计计划

## 目标
将综合评估改造成专业的医疗报告系统，作为家庭干预与医院主治医生之间的桥梁。

## 参考标准
基于专业孤独症评估报告（ADOS、ADI-R等）的格式，包含：
- 发育史
- 当前功能水平
- 家庭干预记录
- 兴趣档案分析
- 能力发展轨迹
- 临床建议

## 实施步骤

### 阶段1：Schema 和类型定义 ✅
- [x] 创建 `comprehensiveAssessmentSchemas.ts`
- [ ] 更新 `types/index.ts` 添加新类型

### 阶段2：Agent 服务层（React 模式）
- [ ] 创建 `comprehensiveAssessmentAgent.ts`
  - 实现 React 模式（类似 gameRecommendConversationalAgent）
  - 集成 memory fetch 工具
  - 集成 knowledge fetch 工具
  - 定义 Qwen Function Calling schema

### 阶段3：Prompt 工程
- [ ] 设计专业的系统提示词
  - 医疗报告写作规范
  - 数据分析方法
  - 临床建议生成逻辑

### 阶段4：UI 组件
- [ ] 创建报告卡片组件（聊天页面）
  - 简略信息展示
  - 点击跳转功能
- [ ] 创建完整报告组件（档案页面）
  - 专业报告布局
  - 可打印格式
  - 导出功能

### 阶段5：集成和测试
- [ ] 集成到 Chatbot
- [ ] 集成到档案页面
- [ ] 端到端测试

## 文件清单

### 新建文件
1. `frontend/src/services/comprehensiveAssessmentSchemas.ts` ✅
2. `frontend/src/services/comprehensiveAssessmentAgent.ts`
3. `frontend/src/components/AssessmentReportCard.tsx`
4. `frontend/src/components/ComprehensiveAssessmentReport.tsx`

### 修改文件
1. `frontend/src/types/index.ts`
2. `frontend/src/App.tsx` (Chatbot 集成)
3. `frontend/src/App.tsx` (档案页面集成)
4. `frontend/src/services/qwenSchemas.ts` (添加新工具)

## 下一步
请确认是否继续完成所有阶段，或者分批次进行。
