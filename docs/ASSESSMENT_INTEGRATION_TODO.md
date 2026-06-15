# 综合评估系统集成待办事项

## 已完成 ✅

1. Schema 定义
   - `comprehensiveAssessmentSchemas.ts`
   - 更新 `types/index.ts`

2. Agent 服务层
   - `comprehensiveAssessmentAgent.ts` (React 模式)
   - 集成 memory 和 knowledge 工具

3. UI 组件
   - `AssessmentReportCard.tsx` (聊天页面卡片)
   - `ComprehensiveAssessmentReport.tsx` (完整报告)

## 待完成 ⏳

### 1. 更新 Qwen Schemas
文件：`frontend/src/services/qwenSchemas.ts`

添加综合评估工具到 Function Calling schema：

```typescript
export const COMPREHENSIVE_ASSESSMENT_TOOL = {
  type: 'function' as const,
  function: {
    name: 'generate_comprehensive_assessment',
    description: '生成专业的综合评估报告，提交给医生',
    parameters: {
      type: 'object',
      properties: {
        reportingPeriod: {
          type: 'string',
          description: '报告周期，例如："最近3个月"'
        }
      }
    }
  }
};
```

### 2. 集成到 Chatbot (App.tsx)

#### 2.1 导入组件和服务
```typescript
import { generateComprehensiveAssessment } from './services/comprehensiveAssessmentAgent';
import { AssessmentReportCard } from './components/AssessmentReportCard';
import type { ComprehensiveAssessmentReport } from './types';
```

#### 2.2 添加状态管理
```typescript
const [comprehensiveReports, setComprehensiveReports] = useState<ComprehensiveAssessmentReport[]>([]);
const [isGeneratingReport, setIsGeneratingReport] = useState(false);
```

#### 2.3 在 onToolCall 中处理
```typescript
case 'generate_comprehensive_assessment':
  setIsGeneratingReport(true);
  try {
    const report = await generateComprehensiveAssessment({
      childProfile,
      interestProfile,
      abilityProfile,
      reportingPeriod: args.reportingPeriod,
      onProgress: (step, message) => {
        // 显示进度
      }
    });
    
    setComprehensiveReports(prev => [...prev, report]);
    
    // 显示卡片标记
    fullResponse += `\n\n:::ASSESSMENT_REPORT:::${JSON.stringify({
      reportId: report.reportId,
      childName: report.childName,
      assessmentDate: report.assessmentDate
    })}:::`;
  } finally {
    setIsGeneratingReport(false);
  }
  break;
```

#### 2.4 在 parseMessageContent 中解析
```typescript
const assessmentRegex = /:::ASSESSMENT_REPORT:\s*([\s\S]*?)\s*:::/;
const assessmentMatch = text.match(assessmentRegex);
if (assessmentMatch?.[1] && !card) {
  try {
    card = { ...JSON.parse(assessmentMatch[1]), type: 'ASSESSMENT_REPORT' };
  } catch (e) {}
}
```

#### 2.5 在消息渲染中显示卡片
```typescript
{card && card.type === 'ASSESSMENT_REPORT' && (
  <AssessmentReportCard
    report={comprehensiveReports.find(r => r.reportId === card.reportId)!}
    onClick={() => {
      // 跳转到档案页面
      setPage(Page.PROFILE);
      // 触发显示报告
      setSelectedReport(card.reportId);
    }}
  />
)}
```

### 3. 集成到档案页面 (App.tsx - PageProfile)

#### 3.1 添加报告列表显示
在档案页面添加"综合评估报告"标签页：

```typescript
const [selectedReport, setSelectedReport] = useState<string | null>(null);

// 在档案页面UI中添加
<div className="mb-6">
  <h3 className="text-lg font-bold text-gray-800 mb-3">综合评估报告</h3>
  <div className="space-y-3">
    {comprehensiveReports.map(report => (
      <div
        key={report.reportId}
        onClick={() => setSelectedReport(report.reportId)}
        className="bg-white p-4 rounded-lg border-2 border-gray-200 hover:border-primary cursor-pointer transition"
      >
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-semibold text-gray-800">{report.reportingPeriod}</h4>
            <p className="text-sm text-gray-600">{report.assessmentDate}</p>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400" />
        </div>
      </div>
    ))}
  </div>
</div>

{/* 显示完整报告 */}
{selectedReport && (
  <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
    <div className="bg-white rounded-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
      <ComprehensiveAssessmentReportView
        report={comprehensiveReports.find(r => r.reportId === selectedReport)!}
        onClose={() => setSelectedReport(null)}
      />
    </div>
  </div>
)}
```

### 4. 数据持久化

#### 4.1 创建存储服务
文件：`frontend/src/services/assessmentStorage.ts`

```typescript
const STORAGE_KEY = 'comprehensive_assessments';

export const assessmentStorage = {
  save: (report: ComprehensiveAssessmentReport) => {
    const reports = assessmentStorage.getAll();
    reports.push(report);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(reports));
  },
  
  getAll: (): ComprehensiveAssessmentReport[] => {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  },
  
  getById: (id: string) => {
    return assessmentStorage.getAll().find(r => r.reportId === id);
  }
};
```

#### 4.2 在 App.tsx 中加载
```typescript
useEffect(() => {
  const savedReports = assessmentStorage.getAll();
  setComprehensiveReports(savedReports);
}, []);
```

### 5. 测试清单

- [ ] 生成报告功能正常
- [ ] 卡片显示正确
- [ ] 点击卡片跳转到档案页面
- [ ] 完整报告显示正确
- [ ] 打印功能正常
- [ ] 导出功能正常
- [ ] 数据持久化正常
- [ ] Memory 工具调用正常
- [ ] Knowledge 工具调用正常

## 预计工作量

- 集成到 Chatbot: 1-2小时
- 集成到档案页面: 1小时
- 数据持久化: 30分钟
- 测试和调试: 1-2小时

总计：约 4-6 小时

## 注意事项

1. 确保 memory 和 RAG 服务正常运行
2. 测试大量数据时的性能
3. 考虑报告生成的错误处理
4. 添加加载状态和进度提示
5. 考虑报告的版本管理
