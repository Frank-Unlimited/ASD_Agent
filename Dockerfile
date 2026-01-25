# 使用官方Node.js镜像
FROM node:18-slim

# 设置工作目录
WORKDIR /app

# 复制backend目录
COPY backend/package*.json ./

# 安装所有依赖（包括devDependencies，用于构建）
RUN npm install

# 复制源代码
COPY backend/ ./

# 构建TypeScript代码
RUN npm run build

# 初始化数据库
RUN npm run init-db || true

# 删除devDependencies以减小镜像大小
RUN npm prune --production

# 暴露7860端口（魔搭创空间要求）
EXPOSE 7860

# 启动应用
CMD ["npm", "start"]
