# ASD地板时光干预辅助系统 - UML时序图描述

本文档提供系统核心流程的时序图文字描述，可直接用于AI画图工具生成UML时序图。

---

## 时序图1：用户注册登录流程

**参与者**：
- 家长（用户）
- 前端系统
- 后端API
- 短信服务
- 数据库

**流程描述**：

1. 家长打开APP，进入登录页面
2. 家长输入手机号，点击"获取验证码"
3. 前端系统发送请求到后端API：POST /api/auth/send-code
4. 后端API验证手机号格式
5. 后端API调用短信服务发送验证码
6. 短信服务返回发送成功
7. 后端API将验证码存入Redis（5分钟有效期）
8. 后端API返回"验证码已发送"给前端
9. 前端显示"验证码已发送"提示
10. 家长收到短信，输入验证码
11. 家长点击"登录"
12. 前端发送请求到后端API：POST /api/auth/verify-login
13. 后端API从Redis验证验证码
14. 验证码正确，后端查询数据库用户信息
15. 如果用户不存在，创建新用户记录
16. 后端生成JWT Token
17. 后端返回Token和用户信息给前端
18. 前端存储Token到本地
19. 前端跳转到主页

---

## 时序图2：初次评估流程

**参与者**：
- 家长
- 前端系统
- 后端API
- 初评估Agent
- LangGraph工作流
- 数据库
- Graphiti记忆系统

**流程描述**：

1. 家长进入"初次评估"页面
2. 家长选择评估方式：导入医院报告或填写内置量表
3. 家长上传医院报告PDF文件
4. 前端发送请求：POST /api/assessments/import
5. 后端API接收文件，保存到临时目录
6. 后端API触发LangGraph工作流
7. LangGraph调用初评估Agent
8. 初评估Agent使用GPT-4V解析PDF内容
9. 初评估Agent提取结构化数据（CARS-2、ADOS-2量表分数）
10. 初评估Agent分析质性描述，提取行为细节
11. 初评估Agent动态创建观察维度（基于孩子特点）
12. 初评估Agent设置变化检测阈值
13. 初评估Agent生成初始State（childTimeline）
14. LangGraph将State保存到数据库
15. LangGraph调用Graphiti记忆系统
16. Graphiti创建孩子的基础记忆节点
17. Graphiti返回记忆ID
18. LangGraph返回评估结果给后端API
19. 后端API返回评估报告给前端
20. 前端展示评估结果：能力雷达图、观察清单、初期目标
21. 家长确认评估结果
22. 系统自动跳转到游戏推荐页面

---

## 时序图3：游戏推荐流程

**参与者**：
- 家长
- 前端系统
- 后端API
- 推荐Agent
- 变化检测Agent
- LangGraph工作流
- PostgreSQL向量数据库
- 数据库

**流程描述**：

1. 家长进入"游戏推荐"页面
2. 前端发送请求：POST /api/recommendations
3. 后端API触发LangGraph工作流
4. LangGraph首先调用变化检测Agent
5. 变化检测Agent从数据库读取最近观察记录
6. 变化检测Agent分析趋势（Mann-Kendall检验）
7. 变化检测Agent识别进步维度和短板维度
8. 变化检测Agent更新State.currentContext.recentTrends
9. LangGraph调用推荐Agent
10. 推荐Agent读取State中的最新趋势
11. 推荐Agent计算各维度优先级分数
12. 推荐Agent生成查询向量（基于孩子特点）
13. 推荐Agent调用PostgreSQL向量数据库
14. 向量数据库执行相似度搜索（pgvector）
15. 向量数据库返回候选游戏列表（Top 20）
16. 推荐Agent对候选游戏进行多目标优化评分
17. 推荐Agent为每个游戏生成推荐理由
18. 推荐Agent选择Top 3游戏
19. 推荐Agent更新State.currentContext.selectedGames
20. LangGraph保存State到数据库
21. LangGraph返回推荐结果给后端API
22. 后端API返回推荐游戏列表给前端
23. 前端展示游戏卡片（名称、目标、推荐理由、玩法）
24. 家长选择一个游戏，点击"开始游戏"

---

## 时序图4：游戏干预会话流程（核心流程）

**参与者**：
- 家长
- 前端系统
- 后端API
- 实时指引Agent
- 观察捕获Agent
- LangGraph工作流
- WebSocket服务
- 视频录制模块
- 数据库

**流程描述**：

1. 家长点击"开始游戏"
2. 前端发送请求：POST /api/sessions
3. 后端API创建新会话记录
4. 后端API触发LangGraph工作流
5. LangGraph初始化currentSession State
6. LangGraph调用实时指引Agent
7. 实时指引Agent生成游戏步骤列表
8. 实时指引Agent准备语音指引内容
9. 后端API返回sessionId和初始指引
10. 前端建立WebSocket连接：/api/ws/guidance/:sessionId
11. WebSocket连接成功
12. 前端启动视频录制
13. 前端播放第一步语音指引："准备好积木，坐在孩子旁边"
14. 家长按照指引操作
15. 家长点击"下一步"
16. 前端通过WebSocket发送：next_step
17. 实时指引Agent接收消息
18. 实时指引Agent发送第二步指引
19. WebSocket推送语音内容给前端
20. 前端播放语音："把积木递给孩子，观察他的反应"
21. 孩子微笑了
22. 家长点击快捷按钮[😊 微笑]
23. 前端通过WebSocket发送：quick_record {type: "smile", timestamp: "14:32:15"}
24. 观察捕获Agent接收记录
25. 观察捕获Agent创建ObservationEvent
26. 观察捕获Agent保存到State.currentSession.realTimeObservations
27. 观察捕获Agent分析重要性
28. 观察捕获Agent通过WebSocket推送提示："孩子笑了！这是很好的信号"
29. 前端显示Toast提示
30. 游戏继续进行（重复步骤16-29）
31. 15分钟后，家长点击"结束游戏"
32. 前端停止视频录制
33. 前端上传视频文件：POST /api/videos/upload
34. 后端API保存视频文件
35. 后端API返回videoId
36. 前端发送请求：PUT /api/sessions/:id/end
37. 后端API更新会话状态为"ended"
38. 后端API触发异步视频分析任务
39. 后端API返回"会话已结束"
40. 前端跳转到"会话总结"页面

---

## 时序图5：视频分析与会话总结流程

**参与者**：
- 后端API
- 视频分析Agent
- 总结Agent
- 反馈表Agent
- LangGraph工作流
- OpenAI GPT-4V
- FFmpeg
- 数据库

**流程描述**：

1. 后端API触发异步视频分析任务
2. 视频分析Agent从队列获取任务
3. 视频分析Agent使用FFmpeg提取关键帧（每秒1帧）
4. FFmpeg返回帧图片列表
5. 视频分析Agent调用OpenAI GPT-4V
6. GPT-4V分析每一帧：表情、眼神、肢体动作
7. GPT-4V返回分析结果
8. 视频分析Agent识别关键时刻（首次出现、情绪变化）
9. 视频分析Agent生成视频片段标注
10. 视频分析Agent更新State.currentSession.videoAnalysis
11. 视频分析Agent标记任务完成
12. LangGraph检测到视频分析完成
13. LangGraph调用总结Agent
14. 总结Agent读取State中的所有数据：
    - realTimeObservations（快捷按钮记录）
    - videoAnalysis（AI视频分析）
    - guidanceLog（指引历史）
15. 总结Agent融合多源数据
16. 总结Agent生成会话总结：
    - 本次亮点（3-5个）
    - 进步表现
    - 需要关注的点
    - 孩子的情绪状态
17. 总结Agent更新State.currentSession.sessionSummary
18. LangGraph调用反馈表Agent
19. 反馈表Agent基于会话总结生成个性化问题
20. 反馈表Agent生成3-5个问题（单选/多选）
21. 反馈表Agent更新State.currentSession.feedbackForm
22. LangGraph设置State.waitForUser = true
23. LangGraph保存Checkpoint
24. 后端API通知前端："总结已生成"
25. 前端轮询或WebSocket接收通知
26. 前端请求：GET /api/sessions/:id/summary
27. 后端API返回会话总结和反馈表
28. 前端展示会话总结页面
29. 前端展示反馈表

---

## 时序图6：家长反馈与记忆更新流程

**参与者**：
- 家长
- 前端系统
- 后端API
- 记忆更新Agent
- 再评估Agent
- LangGraph工作流
- Graphiti记忆系统
- 数据库

**流程描述**：

1. 家长阅读会话总结
2. 家长填写反馈表（3-5个问题）
3. 家长点击"提交反馈"
4. 前端发送请求：POST /api/feedback/:sessionId/submit
5. 后端API接收反馈数据
6. 后端API从数据库加载Checkpoint
7. 后端API恢复State
8. 后端API更新State.currentSession.parentFeedback
9. 后端API设置State.waitForUser = false
10. 后端API触发LangGraph继续执行
11. LangGraph调用记忆更新Agent
12. 记忆更新Agent读取所有新观察数据
13. 记忆更新Agent调用Graphiti API
14. Graphiti为每个观察创建记忆节点
15. Graphiti建立节点之间的关联关系
16. Graphiti执行时序分析
17. Graphiti检测里程碑事件
18. Graphiti返回更新后的记忆网络
19. 记忆更新Agent更新State.childTimeline.microObservations
20. 记忆更新Agent更新State.childTimeline.metrics（新增dataPoints）
21. LangGraph调用再评估Agent
22. 再评估Agent读取全部历史数据
23. 再评估Agent对比基线数据
24. 再评估Agent计算各维度进展百分比
25. 再评估Agent分析趋势（improving/stable/declining）
26. 再评估Agent识别需要调整的维度
27. 再评估Agent生成下一步建议
28. 再评估Agent更新State.currentContext.reEvaluation
29. LangGraph判断是否需要调整策略
30. 如果需要调整，LangGraph跳转到推荐Agent节点
31. 如果不需要调整，LangGraph继续当前计划
32. LangGraph保存最终State到数据库
33. LangGraph返回结果给后端API
34. 后端API返回"反馈已提交"给前端
35. 前端显示"感谢反馈"提示
36. 前端跳转到主页，显示最新进展

---

## 时序图7：微观变化捕捉 - 语音记录流程

**参与者**：
- 家长
- 前端系统
- 后端API
- 观察捕获Agent
- 变化检测Agent
- LangGraph工作流
- OpenAI GPT-4
- 数据库

**流程描述**：

1. 家长在任意页面点击"记录观察"按钮
2. 前端打开语音录制弹窗
3. 家长点击"开始录音"
4. 前端调用浏览器录音API
5. 家长说："今天玩积木时，辰辰突然抬头看了我一眼，大概2秒"
6. 家长点击"停止录音"
7. 前端生成音频文件（WebM格式）
8. 前端发送请求：POST /api/observations/voice
9. 后端API接收音频文件
10. 后端API调用OpenAI Whisper API转文字
11. Whisper返回文字："今天玩积木时，辰辰突然抬头看了我一眼，大概2秒"
12. 后端API触发LangGraph工作流
13. LangGraph调用观察捕获Agent
14. 观察捕获Agent调用GPT-4分析文本
15. GPT-4提取结构化信息：
    - timestamp: 当前时间
    - context: "积木游戏中"
    - behavior: "主动眼神接触"
    - duration: "约2秒"
    - significance: 待分析
16. 观察捕获Agent创建ObservationRecord
17. LangGraph调用变化检测Agent
18. 变化检测Agent查询历史记录
19. 数据库返回过去30天的眼神接触记录
20. 变化检测Agent分析：这是首次"主动"眼神接触
21. 变化检测Agent标记significance: "breakthrough"
22. 变化检测Agent创建Milestone记录
23. 变化检测Agent生成庆祝消息："🌟 这是孩子的第一次主动眼神接触！"
24. 变化检测Agent更新State
25. LangGraph保存State到数据库
26. LangGraph返回分析结果给后端API
27. 后端API返回结构化记录和里程碑提示
28. 前端显示分析结果卡片
29. 前端弹出庆祝动画和提示
30. 家长点击"查看详情"
31. 前端跳转到观察历史页面，高亮显示这条记录

---

## 时序图8：成长可视化与报告导出流程

**参与者**：
- 家长
- 前端系统
- 后端API
- 可视化Agent
- LangGraph工作流
- Graphiti记忆系统
- 数据库
- PDF生成服务

**流程描述**：

1. 家长进入"成长历程"页面
2. 前端发送请求：GET /api/visualizations/:childId/radar
3. 后端API查询数据库，获取最新metrics数据
4. 后端API计算六大维度的当前分数
5. 后端API返回雷达图数据
6. 前端使用ECharts渲染雷达图
7. 家长点击"查看时间线"
8. 前端发送请求：GET /api/visualizations/:childId/timeline
9. 后端API触发LangGraph工作流
10. LangGraph调用可视化Agent
11. 可视化Agent查询Graphiti记忆系统
12. Graphiti返回所有里程碑事件（按时间排序）
13. 可视化Agent为每个里程碑生成展示数据
14. 可视化Agent返回时间线数据
15. 后端API返回时间线数据给前端
16. 前端渲染时间线视图（带视频片段）
17. 家长点击"导出报告"
18. 前端弹出选项：医学报告 / 家长报告
19. 家长选择"医学报告"
20. 前端发送请求：GET /api/export/:childId/medical
21. 后端API触发LangGraph工作流
22. LangGraph调用可视化Agent
23. 可视化Agent收集所有数据：
    - 基础信息
    - 评估历史
    - 干预时间线
    - 能力变化趋势
    - 里程碑事件
    - 视频片段截图
24. 可视化Agent生成报告结构
25. 可视化Agent调用PDF生成服务
26. PDF生成服务使用模板渲染
27. PDF生成服务返回PDF文件
28. 后端API返回PDF下载链接
29. 前端触发下载
30. 家长保存PDF文件到手机

---

## 时序图9：医生查看患儿数据流程（V2.0功能）

**参与者**：
- 医生
- 医生端前端
- 后端API
- 数据库
- Graphiti记忆系统

**流程描述**：

1. 医生登录医生端系统
2. 医生进入"患儿列表"页面
3. 前端发送请求：GET /api/doctor/patients
4. 后端API查询数据库，获取该医生关联的患儿列表
5. 数据库返回患儿基础信息
6. 后端API返回患儿列表给前端
7. 前端展示患儿卡片（姓名、年龄、最近干预时间）
8. 医生点击某个患儿"查看详情"
9. 前端发送请求：GET /api/doctor/patients/:childId/detail
10. 后端API查询数据库，获取患儿完整档案
11. 后端API查询Graphiti，获取记忆网络
12. 后端API汇总数据：
    - 基础信息
    - 评估历史
    - 干预记录（最近30天）
    - 能力趋势图
    - 里程碑事件
13. 后端API返回详细数据
14. 前端展示患儿详情页面
15. 医生查看雷达图，发现"双向沟通"维度较低
16. 医生点击"给出建议"
17. 前端打开建议输入框
18. 医生输入："建议增加躲猫猫游戏，每天2次，每次10分钟"
19. 医生点击"提交建议"
20. 前端发送请求：POST /api/doctor/patients/:childId/advice
21. 后端API保存医生建议到数据库
22. 后端API通知家长端（推送通知）
23. 后端API返回"建议已提交"
24. 前端显示成功提示
25. 家长端收到推送："医生给出了新建议"
26. 家长打开APP查看建议
27. 系统自动将建议转化为游戏计划

---

## 时序图10：系统异常处理流程

**参与者**：
- 家长
- 前端系统
- 后端API
- LangGraph工作流
- 数据库
- 日志系统

**流程描述**：

1. 家长正在进行游戏会话
2. 网络突然断开
3. WebSocket连接中断
4. 前端检测到连接断开
5. 前端将当前State保存到LocalStorage
6. 前端显示"网络断开，数据已保存"提示
7. 网络恢复
8. 前端自动重连WebSocket
9. 前端发送请求：POST /api/sessions/:id/resume
10. 后端API从数据库加载Checkpoint
11. 后端API对比前端State和服务端State
12. 后端API合并数据（以最新时间戳为准）
13. 后端API返回合并后的State
14. 前端恢复会话状态
15. 前端显示"已恢复会话"提示
16. 游戏继续进行

**异常场景2：视频分析失败**

1. 视频分析Agent调用GPT-4V失败（API超时）
2. Agent捕获异常
3. Agent记录错误日志到日志系统
4. Agent将任务重新放入队列（最多重试3次）
5. Agent更新任务状态为"pending_retry"
6. 后端API通知前端："视频分析中，请稍候"
7. 前端显示加载动画
8. 第二次尝试成功
9. Agent完成分析
10. Agent更新任务状态为"completed"
11. 后端API通知前端："分析完成"
12. 前端刷新页面，显示分析结果

**异常场景3：LangGraph工作流中断**

1. LangGraph执行到记忆更新Agent
2. Graphiti服务突然不可用
3. Agent抛出异常
4. LangGraph捕获异常
5. LangGraph保存当前Checkpoint
6. LangGraph记录错误日志
7. LangGraph返回错误给后端API
8. 后端API返回友好错误提示给前端
9. 前端显示："系统繁忙，请稍后重试"
10. 家长点击"重试"
11. 前端发送请求：POST /api/sessions/:id/retry
12. 后端API从Checkpoint恢复
13. Graphiti服务已恢复
14. LangGraph继续执行
15. 流程正常完成

---

## 使用说明

以上时序图描述可以直接输入到AI画图工具（如ChatGPT、Claude、通义千问等）中，使用以下提示词：

```
请根据以下时序图描述，生成PlantUML格式的时序图代码：

[粘贴上述某个时序图的完整描述]

要求：
1. 使用标准的PlantUML语法
2. 参与者使用participant关键字定义
3. 消息使用箭头表示（-> 或 -->）
4. 添加适当的注释和分组
5. 使用激活/停用表示处理过程
```

或者使用Mermaid格式：

```
请根据以下时序图描述，生成Mermaid格式的时序图代码：

[粘贴上述某个时序图的完整描述]

要求：
1. 使用sequenceDiagram语法
2. 清晰标注参与者
3. 使用箭头表示消息流向
4. 添加Note注释说明关键步骤
```

---

*文档版本：v1.0*
*最后更新：2025-01-26*
