# Prompts 管理

本目录统一管理所有 AI 提示词（Prompts），便于维护和优化。

## 📁 文件结构

```
prompts/
├── index.ts                      # 统一导出
├── asd-report-analysis.ts       # ASD 报告分析
├── multimodal-analysis.ts       # 多模态分析（图片/视频）
├── diagnosis-analysis.ts        # 诊断分析（医疗报告/口述）
└── README.md                    # 本文档
```

## 📝 Prompt 列表

### 1. ASD 报告分析
**文件**: `asd-report-analysis.ts`  
**导出**: `ASD_REPORT_ANALYSIS_PROMPT`  
**用途**: 分析医疗评估报告图片，提取 OCR 文字、生成摘要和孩子画像  
**输出格式**: JSON
```json
{
  "ocr": "文字提取结果",
  "summary": "报告摘要（一句话）",
  "profile": "孩子画像（一段话）"
}
```

### 2. 默认图片分析
**文件**: `multimodal-analysis.ts`  
**导出**: `DEFAULT_IMAGE_ANALYSIS_PROMPT`  
**用途**: 分析儿童行为图片，识别场景、人物、活动、行为等  
**输出格式**: 结构化文本

### 3. 默认视频分析
**文件**: `multimodal-analysis.ts`  
**导出**: `DEFAULT_VIDEO_ANALYSIS_PROMPT`  
**用途**: 分析儿童行为视频，观察互动质量、时间线、发展能力等  
**输出格式**: 结构化文本

### 4. 医疗报告分析
**文件**: `diagnosis-analysis.ts`  
**导出**: `MEDICAL_REPORT_ANALYSIS_PROMPT`  
**用途**: 分析医疗报告文本，提取核心症状、能力评估等  
**输出格式**: 300字以内的专业描述  
**占位符**: `{reportContent}` - 报告内容

### 5. 家长口述分析
**文件**: `diagnosis-analysis.ts`  
**导出**: `VERBAL_DESCRIPTION_ANALYSIS_PROMPT`  
**用途**: 根据家长描述分析孩子情况，生成温和的专业评估  
**输出格式**: 300字以内的温和描述  
**占位符**: `{verbalDescription}` - 家长描述内容

## 🔧 使用方法

### 基本导入
```typescript
// 导入单个 Prompt
import { ASD_REPORT_ANALYSIS_PROMPT } from './prompts';

// 导入多个 Prompts
import { 
  DEFAULT_IMAGE_ANALYSIS_PROMPT, 
  DEFAULT_VIDEO_ANALYSIS_PROMPT 
} from './prompts';
```

### 使用占位符
某些 Prompt 包含占位符，需要替换后使用：

```typescript
import { MEDICAL_REPORT_ANALYSIS_PROMPT } from './prompts';

// 替换占位符
const prompt = MEDICAL_REPORT_ANALYSIS_PROMPT.replace(
  '{reportContent}', 
  actualReportText
);

// 发送给 AI
const response = await sendToAI(prompt);
```

### 在服务中使用
```typescript
// multimodalService.ts
import { DEFAULT_IMAGE_ANALYSIS_PROMPT } from '../prompts/multimodal-analysis';

class MultimodalService {
  async parseImage(file: File, customPrompt?: string) {
    const prompt = customPrompt || DEFAULT_IMAGE_ANALYSIS_PROMPT;
    // ...
  }
}
```

## ✏️ 编写规范

### 1. Prompt 结构
- **角色定义**: 明确 AI 的角色（如"专业的 ASD 儿童行为分析师"）
- **任务说明**: 清晰描述需要完成的任务
- **输出要求**: 指定输出格式、字数限制、结构要求
- **注意事项**: 特殊要求或限制

### 2. 命名规范
- 使用 `UPPER_SNAKE_CASE` 命名常量
- 名称应清晰表达用途
- 示例：`ASD_REPORT_ANALYSIS_PROMPT`、`DEFAULT_IMAGE_ANALYSIS_PROMPT`

### 3. 文档注释
每个 Prompt 都应包含 JSDoc 注释：
```typescript
/**
 * ASD 报告分析 Prompt
 * 用于分析医疗评估报告图片，提取文字、生成摘要和孩子画像
 */
export const ASD_REPORT_ANALYSIS_PROMPT = `...`;
```

### 4. 占位符规范
- 使用 `{variableName}` 格式
- 在注释中说明占位符含义
- 示例：`{reportContent}` - 报告内容

## 🎯 优化建议

### 提高准确性
1. **明确角色**: 给 AI 一个专业的角色定位
2. **结构化输出**: 使用编号列表、JSON 格式等
3. **示例引导**: 在 Prompt 中提供输出示例
4. **限制范围**: 明确不要做什么

### 提高效率
1. **精简语言**: 去除冗余描述
2. **关键词突出**: 使用加粗、编号等
3. **分步骤**: 将复杂任务分解为步骤

### 提高可维护性
1. **模块化**: 将相关 Prompts 放在同一文件
2. **复用**: 提取公共部分为变量
3. **版本控制**: 重大修改时保留旧版本注释

## 📊 Prompt 效果评估

定期评估 Prompt 效果：
1. **准确性**: AI 输出是否符合预期
2. **稳定性**: 多次调用结果是否一致
3. **效率**: Token 使用量是否合理
4. **用户反馈**: 实际使用中的问题

## 🔄 更新流程

1. **修改 Prompt**: 在对应文件中修改
2. **测试验证**: 使用真实数据测试
3. **更新文档**: 更新本 README
4. **代码审查**: 提交前进行审查
5. **版本记录**: 在 Git 提交信息中说明修改原因

## 📚 参考资源

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library)
- [Google AI Prompt Best Practices](https://ai.google.dev/docs/prompt_best_practices)

## 🐛 常见问题

### Q: Prompt 太长会影响性能吗？
A: 会。尽量精简，保持在 1000-2000 tokens 以内。

### Q: 如何测试 Prompt 效果？
A: 使用多个真实案例测试，观察输出的准确性和一致性。

### Q: 可以在 Prompt 中使用中文吗？
A: 可以。对于中文场景，使用中文 Prompt 通常效果更好。

### Q: 如何处理 AI 输出格式不一致？
A: 在 Prompt 中明确要求输出格式，使用 JSON Schema 或示例引导。
