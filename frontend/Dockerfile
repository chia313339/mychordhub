# 前端 Dockerfile - Vue.js + TypeScript + Vite
FROM node:20-alpine as development

# 設置工作目錄
WORKDIR /app

# 複製package文件並安裝依賴
COPY package*.json ./
RUN npm install

# 複製源碼
COPY . .

# 暴露端口
EXPOSE 3000

# 開發模式啟動命令
CMD ["npm", "run", "dev"]

# 生產構建階段
FROM node:20-alpine as build

WORKDIR /app

# 安裝依賴
COPY package*.json ./
RUN npm ci --only=production

# 複製源碼並構建
COPY . .
RUN npm run build

# 生產運行階段
FROM nginx:alpine as production

# 複製構建結果到nginx
COPY --from=build /app/dist /usr/share/nginx/html

# 複製nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 啟動nginx
CMD ["nginx", "-g", "daemon off;"]