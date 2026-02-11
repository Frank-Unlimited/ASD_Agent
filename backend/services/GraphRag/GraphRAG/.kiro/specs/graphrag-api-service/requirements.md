# Requirements Document

## Introduction

本文档定义了将 Microsoft GraphRAG 项目开发为生产级 API 服务的需求。GraphRAG 是一个基于知识图谱的检索增强生成（RAG）系统，当前已有基础的 API 实现，需要将其改造为可部署、可扩展、易维护的服务架构，支持多种查询方式（local、global、drift、basic），并提供完整的 RESTful API 接口。

## Glossary

- **GraphRAG**: Graph-based Retrieval-Augmented Generation，基于知识图谱的检索增强生成系统
- **API Service**: 对外提供 HTTP/HTTPS 接口的应用程序接口服务
- **FastAPI**: 现代、快速的 Python Web 框架，用于构建 API
- **Query Engine**: 查询引擎，负责处理不同类型的 GraphRAG 查询
- **Index Data**: 索引数据，包括实体、关系、社区、文本单元等预处理的知识图谱数据
- **Local Search**: 本地搜索，基于特定实体和关系的精确查询
- **Global Search**: 全局搜索，基于整体社区结构的宏观查询
- **Drift Search**: 漂移搜索，结合本地和全局特性的混合查询
- **Basic Search**: 基础搜索，基于文本单元的简单查询
- **Streaming Response**: 流式响应，逐步返回查询结果而非一次性返回
- **Configuration Management**: 配置管理，管理服务运行所需的各种配置参数
- **Health Check**: 健康检查，用于监控服务运行状态的接口
- **CORS**: Cross-Origin Resource Sharing，跨域资源共享
- **Conda Environment**: Conda 虚拟环境，用于隔离 Python 项目依赖

## Requirements

### Requirement 1

**User Story:** 作为 API 用户，我希望能够通过 HTTP 接口执行 GraphRAG 查询，以便在我的应用中集成知识图谱检索能力

#### Acceptance Criteria

1. WHEN 用户发送 POST 请求到 `/api/query` 端点 THEN API Service SHALL 接受包含查询文本和查询类型的 JSON 请求体
2. WHEN 用户发送 GET 请求到 `/api/query` 端点 THEN API Service SHALL 接受查询参数并返回查询结果
3. WHEN Query Engine 处理查询请求 THEN API Service SHALL 支持 local、global、drift、basic 四种查询类型
4. WHEN 查询成功完成 THEN API Service SHALL 返回包含查询结果、查询类型和上下文信息的 JSON 响应
5. WHEN 查询参数无效 THEN API Service SHALL 返回 400 状态码和错误描述

### Requirement 2

**User Story:** 作为 API 用户，我希望能够获取流式查询响应，以便实时展示查询进度和结果

#### Acceptance Criteria

1. WHEN 用户发送请求到 `/api/query_stream` 端点 THEN API Service SHALL 以 Server-Sent Events 或分块传输方式返回流式响应
2. WHEN Query Engine 生成查询结果 THEN API Service SHALL 逐步发送结果片段而非等待完整结果
3. WHEN 流式传输过程中发生错误 THEN API Service SHALL 在流中包含错误信息并优雅终止
4. WHEN 流式传输完成 THEN API Service SHALL 发送结束标记

### Requirement 3

**User Story:** 作为系统管理员，我希望服务能够自动加载和缓存索引数据，以便提高查询响应速度

#### Acceptance Criteria

1. WHEN API Service 启动 THEN Configuration Management SHALL 从配置文件加载 GraphRAG 配置
2. WHEN API Service 初始化 THEN Query Engine SHALL 预加载实体、关系、社区、文本单元等索引数据到内存
3. WHEN Index Data 加载完成 THEN API Service SHALL 缓存数据以供后续查询使用
4. WHEN Index Data 加载失败 THEN API Service SHALL 记录详细错误日志并拒绝查询请求
5. WHEN 多个查询请求到达 THEN API Service SHALL 复用已缓存的 Index Data

### Requirement 4

**User Story:** 作为系统管理员，我希望能够通过配置文件管理服务参数，以便灵活调整服务行为

#### Acceptance Criteria

1. WHEN 管理员修改配置文件 THEN Configuration Management SHALL 支持通过环境变量覆盖默认配置
2. WHEN API Service 启动 THEN Configuration Management SHALL 读取项目根目录、数据目录、日志目录等路径配置
3. WHEN Configuration Management 加载配置 THEN API Service SHALL 验证必需配置项的存在性和有效性
4. WHEN 配置无效 THEN API Service SHALL 拒绝启动并输出清晰的错误信息
5. WHEN 配置包含敏感信息 THEN Configuration Management SHALL 支持从 .env 文件读取 API 密钥等敏感数据

### Requirement 5

**User Story:** 作为运维人员，我希望服务提供健康检查和监控接口，以便监控服务运行状态

#### Acceptance Criteria

1. WHEN 监控系统访问 `/api/health` 端点 THEN API Service SHALL 返回服务状态和版本信息
2. WHEN API Service 运行正常 THEN Health Check SHALL 返回 200 状态码和 "ok" 状态
3. WHEN Index Data 未加载 THEN Health Check SHALL 返回 503 状态码和 "not ready" 状态
4. WHEN 监控系统访问 `/api/metrics` 端点 THEN API Service SHALL 返回查询计数、平均响应时间等指标
5. WHEN API Service 记录日志 THEN Configuration Management SHALL 支持配置日志级别和日志输出路径

### Requirement 6

**User Story:** 作为 API 用户，我希望服务支持 CORS，以便从浏览器应用中调用 API

#### Acceptance Criteria

1. WHEN 浏览器发送跨域请求 THEN API Service SHALL 在响应中包含适当的 CORS 头
2. WHEN API Service 配置 CORS THEN Configuration Management SHALL 支持配置允许的来源、方法和头
3. WHEN 浏览器发送预检请求 THEN API Service SHALL 正确响应 OPTIONS 请求
4. WHEN CORS 配置为严格模式 THEN API Service SHALL 仅允许配置的来源访问

### Requirement 7

**User Story:** 作为开发者，我希望服务提供清晰的错误处理和日志记录，以便快速定位和解决问题

#### Acceptance Criteria

1. WHEN 查询过程中发生异常 THEN API Service SHALL 捕获异常并返回适当的 HTTP 状态码
2. WHEN 异常发生 THEN API Service SHALL 记录完整的错误堆栈到日志文件
3. WHEN API Service 记录日志 THEN Configuration Management SHALL 使用结构化日志格式包含时间戳、级别、消息
4. WHEN 日志文件达到大小限制 THEN API Service SHALL 自动轮转日志文件
5. WHEN 用户请求无效 THEN API Service SHALL 返回包含错误详情的 JSON 响应

### Requirement 8

**User Story:** 作为部署工程师，我希望服务易于部署和启动，以便在不同环境中快速部署

#### Acceptance Criteria

1. WHEN 工程师执行启动命令 THEN API Service SHALL 在指定的主机和端口上启动
2. WHEN API Service 启动 THEN Configuration Management SHALL 支持通过命令行参数指定主机和端口
3. WHEN 服务在 Conda Environment 中运行 THEN API Service SHALL 正确识别和使用虚拟环境中的依赖
4. WHEN 服务部署到生产环境 THEN API Service SHALL 支持使用 Gunicorn 或 Uvicorn 作为 ASGI 服务器
5. WHEN 服务需要重启 THEN API Service SHALL 支持优雅关闭，完成正在处理的请求后再退出

### Requirement 9

**User Story:** 作为 API 用户，我希望能够通过 Web 界面测试查询功能，以便快速验证 API 行为

#### Acceptance Criteria

1. WHEN 用户访问根路径 `/` THEN API Service SHALL 提供一个简单的 Web 界面用于测试查询
2. WHEN 用户在 Web 界面输入查询 THEN API Service SHALL 通过 JavaScript 调用后端 API 并展示结果
3. WHEN Web 界面展示结果 THEN API Service SHALL 支持 Markdown 格式渲染
4. WHEN 用户选择流式查询 THEN Web 界面 SHALL 实时展示流式响应的内容

### Requirement 10

**User Story:** 作为系统架构师，我希望服务具有良好的性能和可扩展性，以便支持高并发查询

#### Acceptance Criteria

1. WHEN 多个并发请求到达 THEN API Service SHALL 使用异步处理避免阻塞
2. WHEN Query Engine 处理查询 THEN API Service SHALL 复用已加载的 Index Data 避免重复加载
3. WHEN 服务负载增加 THEN API Service SHALL 支持水平扩展部署多个实例
4. WHEN 查询响应时间超过阈值 THEN API Service SHALL 记录慢查询日志
5. WHEN 内存使用超过限制 THEN API Service SHALL 实施内存管理策略避免 OOM

### Requirement 11

**User Story:** 作为 API 用户，我希望 API 提供清晰的文档，以便快速了解如何使用接口

#### Acceptance Criteria

1. WHEN 用户访问 `/docs` 端点 THEN API Service SHALL 提供自动生成的 OpenAPI 文档
2. WHEN 用户查看 API 文档 THEN API Service SHALL 展示所有端点、参数、请求体和响应格式
3. WHEN 用户在文档页面测试 API THEN API Service SHALL 支持通过 Swagger UI 直接发送请求
4. WHEN API 接口变更 THEN API Service SHALL 自动更新 OpenAPI 文档

### Requirement 12

**User Story:** 作为安全工程师，我希望服务实施基本的安全措施，以便保护 API 免受常见攻击

#### Acceptance Criteria

1. WHEN 用户发送请求 THEN API Service SHALL 验证请求体大小限制避免 DoS 攻击
2. WHEN API Service 处理用户输入 THEN Query Engine SHALL 清理和验证输入避免注入攻击
3. WHEN 服务配置认证 THEN API Service SHALL 支持 API Key 或 Bearer Token 认证
4. WHEN 未授权用户访问 THEN API Service SHALL 返回 401 状态码
5. WHEN 服务记录日志 THEN API Service SHALL 避免记录敏感信息如 API 密钥
