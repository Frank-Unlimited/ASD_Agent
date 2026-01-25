# 魔搭创空间部署说明

## 前置准备

**重要**: 需要先将backend目录复制到ASD_Agent项目根目录下

```bash
# 在命令行执行
xcopy /E /I "e:\TencentRecord\xwechat_files\wxid_q3omonsd512m12_8f6b\msg\file\2026-01\backend" "e:\PythonProject\ASD_Agent\backend"
```

或者手动操作：
1. 打开文件资源管理器
2. 复制 `e:\TencentRecord\xwechat_files\wxid_q3omonsd512m12_8f6b\msg\file\2026-01\backend` 目录
3. 粘贴到 `e:\PythonProject\ASD_Agent\` 目录下

## 部署步骤

1. 确保backend目录已经放入项目根目录（见上方"前置准备"）
2. 将整个ASD_Agent项目文件夹拖拽到魔搭创空间的"快速创建并部署"页面
3. 系统会自动识别`ms_deploy.json`配置文件
4. 等待构建和部署完成（预计3-5分钟）

## 配置说明

### ms_deploy.json
- **sdk_type**: docker（使用Docker容器部署）
- **resource_configuration**: platform/2v-cpu-16g-mem（2核CPU，16G内存）
- **port**: 7860（魔搭创空间要求的端口）
- **environment_variables**: 环境变量配置
  - NODE_ENV: production
  - PORT: 7860
  - JWT_SECRET: JWT密钥
  - MOCK_VERIFICATION_CODE: 123456（MVP阶段使用）

### Dockerfile
- 基于Node.js 18镜像
- 自动安装依赖
- 构建TypeScript代码
- 初始化SQLite数据库
- 启动Express服务器

## 访问应用

部署成功后，可以通过以下API端点访问：

### 健康检查
```
GET /api/health
```

### 认证相关
```
POST /api/auth/send-code        # 发送验证码
POST /api/auth/verify-login     # 验证码登录
```

### 评估相关
```
POST /api/assessments/import    # 导入医院报告
```

## 注意事项

1. **OpenAI API Key**: 如需使用AI功能，需要在环境变量中配置`OPENAI_API_KEY`
2. **数据持久化**: SQLite数据库文件存储在容器内，重启后数据会丢失（生产环境需要挂载卷）
3. **端口配置**: 必须使用7860端口，这是魔搭创空间的要求
4. **验证码**: MVP阶段使用固定验证码123456，生产环境需要接入真实短信服务

## 故障排查

### 查看日志
在魔搭创空间界面点击"查看日志" → "运行日志"

### 常见问题

1. **端口冲突**: 确保PORT环境变量设置为7860
2. **依赖安装失败**: 检查package.json是否正确
3. **数据库初始化失败**: 查看init-db脚本是否正常执行

## 本地测试

在部署前可以本地测试Docker镜像：

```bash
# 构建镜像
docker build -t asd-backend .

# 运行容器
docker run -p 7860:7860 -e OPENAI_API_KEY=your-key asd-backend

# 测试API
curl http://localhost:7860/api/health
```
