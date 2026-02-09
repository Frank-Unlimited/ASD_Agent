# GraphRAG 部署指南

## 📋 改动说明

本次优化简化了 Docker 部署流程，用户只需挂载向量数据库目录即可运行。

### 核心改动

#### 1. `.gitignore` - 精确控制版本管理

**改动前：**
```gitignore
data/  # 整个 data 目录被忽略
```

**改动后：**
```gitignore
# 仅忽略大文件和临时文件
data/output/lancedb/      # 向量数据库（体积大）
data/cache/               # 缓存
data/logs/                # 日志
data/input/               # 输入文件（用户上传）
data/pdf_outputs/         # PDF 处理输出
data/pdf_csv_exports/     # CSV 导出
data/update_output/       # 更新输出
data/mineru_output/       # MinerU 输出
```

**保留在仓库中：**
- ✅ `data/.env` - 环境变量模板
- ✅ `data/settings*.yaml` - 配置文件
- ✅ `data/prompts/` - Prompt 模板
- ✅ `data/prompt_turn_output/` - Prompt 调优
- ✅ `data/output/*.parquet` - 实体、关系数据文件

#### 2. `docker-compose.yml` - 简化挂载配置

**改动前：**
```yaml
volumes:
  - ./data:/app/data           # 挂载整个 data 目录
  - ./output:/app/output       # 挂载 output 目录
  - ./index:/app/index         # 挂载 index 目录
```

**改动后：**
```yaml
volumes:
  # 仅挂载向量数据库目录
  - ./data/output:/app/data/output
```

**端口统一：**
- 容器内：80
- 宿主机：8080

#### 3. `README.md` - 更新部署文档

**新增内容：**
- 为什么只挂载向量数据库（GitHub 文件大小限制）
- 详细的目录结构说明
- 三种数据准备方式
- 更新所有 Docker 命令示例

## 🎯 设计理念

### 为什么这样设计？

#### 1. GitHub 文件大小限制
- GitHub 单个文件限制：100 MB
- 仓库推荐大小：< 1 GB
- LanceDB 向量数据库通常：几百 MB 到几 GB
- **解决方案**：向量数据库不上传，用户自己生成或迁移

#### 2. 配置文件版本控制
- 配置文件（settings.yaml、prompts）应该版本控制
- 便于团队协作和配置管理
- 用户可以直接使用仓库中的配置
- **解决方案**：配置文件打包在 Docker 镜像中

#### 3. 简化部署流程
- 用户不需要准备复杂的目录结构
- 只需挂载一个目录即可
- 首次运行自动创建向量数据库
- **解决方案**：最小化挂载，只挂载必需的向量数据库

## 📁 目录结构对比

### 改动前

```
项目/
├── data/                    ❌ 整个目录被 .gitignore
│   ├── settings.yaml        ❌ 无法版本控制
│   ├── prompts/             ❌ 无法版本控制
│   └── output/lancedb/      ❌ 体积大，无法上传
├── output/                  ⚠️ 需要挂载
└── index/                   ⚠️ 需要挂载

用户需要：
1. 准备完整的 data 目录
2. 挂载 3 个目录
3. 自己配置所有文件
```

### 改动后

```
项目/
├── data/                    ✅ 部分在仓库中
│   ├── settings.yaml        ✅ 在仓库中，可版本控制
│   ├── prompts/             ✅ 在仓库中，可版本控制
│   └── output/
│       ├── *.parquet        ✅ 在仓库中（小文件）
│       └── lancedb/         ❌ 不在仓库（大文件）
└── output/                  ✅ 在仓库中（仅配置）

用户需要：
1. 克隆仓库（配置已包含）
2. 挂载 1 个目录（data/output）
3. 配置环境变量（.env）
```

## 🚀 部署流程对比

### 改动前

```bash
# 1. 克隆项目
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG

# 2. 准备 data 目录（复杂）
mkdir -p data/{input,output,cache,logs,prompts,prompt_turn_output}
cp -r /somewhere/prompts data/
cp -r /somewhere/settings.yaml data/

# 3. 配置环境变量
cp .env.example .env
vim .env

# 4. 运行（挂载 3 个目录）
docker run -d \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/index:/app/index \
  --env-file .env \
  ghcr.io/frank-unlimited/graphrag:main
```

### 改动后

```bash
# 1. 克隆项目（配置已包含）
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG

# 2. 创建向量数据库目录
mkdir -p data/output/lancedb

# 3. 配置环境变量
cp .env.example .env
vim .env

# 4. 运行（仅挂载 1 个目录）
docker run -d \
  -v $(pwd)/data/output:/app/data/output \
  --env-file .env \
  ghcr.io/frank-unlimited/graphrag:main
```

## 💡 使用场景

### 场景 1：首次部署

```bash
# 克隆 → 创建目录 → 配置 → 运行
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG
mkdir -p data/output/lancedb
cp .env.example .env && vim .env
docker-compose up -d
```

### 场景 2：迁移现有数据

```bash
# 克隆 → 复制向量数据库 → 运行
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG
cp -r /old/data/output/lancedb ./data/output/
docker-compose up -d
```

### 场景 3：从备份恢复

```bash
# 克隆 → 解压备份 → 运行
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG
tar -xzf lancedb-backup.tar.gz -C ./data/output/
docker-compose up -d
```

## ✅ 优势总结

### 对用户
1. ✅ **部署简单**：只需挂载 1 个目录
2. ✅ **配置现成**：settings.yaml、prompts 已在仓库
3. ✅ **快速启动**：3 步即可运行
4. ✅ **数据安全**：向量数据库持久化

### 对开发者
1. ✅ **版本控制**：配置文件可以版本管理
2. ✅ **团队协作**：配置变更可以 PR
3. ✅ **易于维护**：统一的配置管理
4. ✅ **符合规范**：遵守 GitHub 文件大小限制

### 对项目
1. ✅ **仓库精简**：不包含大文件
2. ✅ **克隆快速**：仓库体积小
3. ✅ **CI/CD 友好**：构建速度快
4. ✅ **可扩展性**：易于添加新配置

## 🔍 技术细节

### Docker 镜像内容

```
Docker 镜像包含：
├── /app/graphrag/              # 应用代码
├── /app/server/                # 服务代码
├── /app/data/                  # 配置文件（只读）
│   ├── .env                    # 环境变量模板
│   ├── settings.yaml           # GraphRAG 配置
│   ├── settings_pdf.yaml       # PDF 配置
│   ├── settings_csv.yaml       # CSV 配置
│   ├── prompts/                # Prompt 模板
│   └── prompt_turn_output/     # Prompt 调优
└── /app/data/output/           # 挂载点（空目录）
    └── lancedb/                # 用户挂载到这里
```

### 挂载机制

```
宿主机                    容器内
./data/output/     →     /app/data/output/
├── lancedb/            ├── lancedb/          # 向量数据库
├── *.parquet           ├── *.parquet         # 实体关系数据
└── stats.json          └── stats.json        # 统计信息
```

### 环境变量处理

```
优先级（从高到低）：
1. docker run --env-file .env        # 运行时环境变量
2. docker-compose.yml environment    # Compose 配置
3. 镜像内 /app/data/.env            # 镜像内置模板
```

## 📝 注意事项

### 1. 首次运行
- 向量数据库目录会自动创建
- 首次索引构建需要时间
- 确保 API 密钥配置正确

### 2. 数据迁移
- 只需复制 `data/output/lancedb/` 目录
- 配置文件已在镜像中，无需复制
- 确保向量数据库版本兼容

### 3. 备份策略
```bash
# 备份向量数据库
tar -czf lancedb-backup-$(date +%Y%m%d).tar.gz data/output/lancedb/

# 恢复
tar -xzf lancedb-backup-20241227.tar.gz -C ./data/output/
```

### 4. 更新配置
如果需要修改配置文件：
```bash
# 方式 1：修改仓库中的配置，重新构建镜像
vim data/settings.yaml
docker-compose build

# 方式 2：挂载配置文件（不推荐）
docker run -v $(pwd)/data/settings.yaml:/app/data/settings.yaml ...
```

## 🎓 最佳实践

1. **使用 docker-compose**：比 docker run 更方便
2. **定期备份**：备份 `data/output/lancedb/` 目录
3. **版本标签**：使用特定版本而非 `latest`
4. **环境隔离**：不同项目使用不同的 data/output 目录
5. **监控日志**：定期检查容器日志

## 🔗 相关文档

- [README.md](README.md) - 完整部署文档
- [RUN_DOCKER.md](RUN_DOCKER.md) - Docker 运行详细指南
- [docker-compose.yml](docker-compose.yml) - Compose 配置文件
- [.gitignore](.gitignore) - Git 忽略规则

---

**更新日期**：2024-12-27  
**版本**：v2.0  
**作者**：GraphRAG Team
