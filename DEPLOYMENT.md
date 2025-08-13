# 🚀 MyChordHub 部署指南

本文檔詳細說明如何部署 MyChordHub 到不同環境。

## 📋 部署前檢查清單

### 系統要求
- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ RAM
- 10GB+ 磁碟空間

### 必要設定
- [ ] 環境變數配置
- [ ] SSL 憑證（生產環境）
- [ ] 資料庫備份策略
- [ ] 監控設定

## 🔧 本地開發環境

### 1. 啟動 Docker Desktop
確保 Docker Desktop 正在運行：

**macOS:**
```bash
# 啟動 Docker Desktop 應用程式
open -a Docker
```

**Windows:**
```powershell
# 啟動 Docker Desktop
start "Docker Desktop"
```

**Linux:**
```bash
# 啟動 Docker daemon
sudo systemctl start docker
```

### 2. 初始化專案
```bash
# 克隆專案
git clone <repository-url>
cd mychordhub

# 複製環境變數
cp .env.example .env

# 一鍵啟動
make install
```

### 3. 驗證部署
```bash
# 檢查服務狀態
make status

# 測試服務
curl http://localhost:8000/api/v1/health
curl http://localhost:3000
```

### 4. 常用開發指令
```bash
# 啟動服務
make dev-up

# 查看日誌
make dev-logs

# 重啟服務
make dev-restart

# 停止服務
make dev-down

# 清理資源
make clean
```

## 🌐 生產環境部署

### 1. 環境準備
```bash
# 建立生產環境目錄
mkdir -p /opt/mychordhub
cd /opt/mychordhub

# 克隆程式碼
git clone <repository-url> .
```

### 2. 環境變數設定
```bash
# 複製並編輯生產環境變數
cp .env.example .env.prod

# 編輯生產設定
nano .env.prod
```

**重要設定項目：**
```bash
# 環境
ENVIRONMENT=production

# 安全金鑰（必須更換）
JWT_SECRET_KEY=your-super-secure-production-key

# 資料庫
DATABASE_URL=postgresql://user:password@db:5432/mychordhub
POSTGRES_PASSWORD=secure-production-password

# CORS（設定正確的域名）
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Redis
REDIS_URL=redis://redis:6379/0

# 前端
VITE_API_BASE_URL=https://api.yourdomain.com
```

### 3. SSL 憑證設定
```bash
# 建立 SSL 目錄
mkdir -p nginx/ssl

# 複製憑證檔案
cp /path/to/your/cert.pem nginx/ssl/
cp /path/to/your/key.pem nginx/ssl/

# 設定權限
chmod 600 nginx/ssl/*
```

### 4. 啟動生產環境
```bash
# 建置生產映像
docker-compose -f docker-compose.prod.yml build

# 啟動服務
docker-compose -f docker-compose.prod.yml up -d

# 檢查狀態
docker-compose -f docker-compose.prod.yml ps
```

## ☁️ 雲端平台部署

### Google Cloud Platform (GCP)

#### 1. 建立 GCP 專案
```bash
# 設定專案 ID
export PROJECT_ID=mychordhub-prod
export REGION=asia-east1

# 建立專案
gcloud projects create $PROJECT_ID

# 設定預設專案
gcloud config set project $PROJECT_ID
```

#### 2. 啟用必要服務
```bash
# 啟用 API
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
```

#### 3. 建立 Cloud SQL 資料庫
```bash
# 建立 PostgreSQL 實例
gcloud sql instances create mychordhub-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION

# 建立資料庫
gcloud sql databases create mychordhub \
    --instance=mychordhub-db

# 設定使用者
gcloud sql users set-password postgres \
    --instance=mychordhub-db \
    --password=secure-password
```

#### 4. 建置並部署到 Cloud Run
```bash
# 建置前端
gcloud builds submit ./frontend \
    --tag gcr.io/$PROJECT_ID/mychordhub-frontend

# 建置後端
gcloud builds submit ./backend \
    --tag gcr.io/$PROJECT_ID/mychordhub-backend

# 部署前端
gcloud run deploy mychordhub-frontend \
    --image gcr.io/$PROJECT_ID/mychordhub-frontend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated

# 部署後端
gcloud run deploy mychordhub-backend \
    --image gcr.io/$PROJECT_ID/mychordhub-backend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL="postgresql://..."
```

### AWS ECS 部署

#### 1. 建立 ECR 儲存庫
```bash
# 建立儲存庫
aws ecr create-repository --repository-name mychordhub-frontend
aws ecr create-repository --repository-name mychordhub-backend

# 取得登入資訊
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
```

#### 2. 建置並推送映像
```bash
# 建置映像
docker build -t mychordhub-frontend ./frontend
docker build -t mychordhub-backend ./backend

# 標記映像
docker tag mychordhub-frontend:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/mychordhub-frontend:latest
docker tag mychordhub-backend:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/mychordhub-backend:latest

# 推送映像
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/mychordhub-frontend:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/mychordhub-backend:latest
```

#### 3. 建立 ECS 服務
建立 `ecs-task-definition.json`：
```json
{
  "family": "mychordhub",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "<account-id>.dkr.ecr.us-west-2.amazonaws.com/mychordhub-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mychordhub",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Docker Swarm 叢集部署

#### 1. 初始化 Swarm
```bash
# 主節點初始化
docker swarm init --advertise-addr <master-ip>

# 工作節點加入
docker swarm join --token <token> <master-ip>:2377
```

#### 2. 建立 Stack 檔案
建立 `docker-stack.yml`：
```yaml
version: '3.8'

services:
  frontend:
    image: mychordhub-frontend:latest
    ports:
      - "80:80"
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  backend:
    image: mychordhub-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mychordhub
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mychordhub
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager

volumes:
  postgres_data:
```

#### 3. 部署 Stack
```bash
# 部署
docker stack deploy -c docker-stack.yml mychordhub

# 檢查服務
docker service ls
docker stack services mychordhub
```

## 📊 監控與維護

### 1. 健康檢查
```bash
# API 健康檢查
curl -f http://localhost:8000/api/v1/health

# 資料庫連線檢查
docker-compose exec backend python -c "from app.db.session import engine; engine.connect()"
```

### 2. 日誌管理
```bash
# 查看應用日誌
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看系統日誌
journalctl -u docker

# 日誌輪轉設定
echo '{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}' > /etc/docker/daemon.json
```

### 3. 備份策略
```bash
# 資料庫備份腳本
#!/bin/bash
BACKUP_DIR="/backup/mychordhub"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 建立備份目錄
mkdir -p $BACKUP_DIR

# 備份資料庫
docker-compose exec -T db pg_dump -U postgres mychordhub > "$BACKUP_DIR/db_$TIMESTAMP.sql"

# 備份檔案（如果有使用者上傳檔案）
tar -czf "$BACKUP_DIR/files_$TIMESTAMP.tar.gz" ./uploads

# 清理舊備份（保留 7 天）
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 4. 自動更新腳本
```bash
#!/bin/bash
# update.sh

# 停止服務
docker-compose down

# 拉取最新程式碼
git pull origin main

# 建置新映像
docker-compose build

# 啟動服務
docker-compose up -d

# 檢查健康狀態
sleep 30
curl -f http://localhost:8000/api/v1/health
```

## 🔒 安全性設定

### 1. 防火牆設定
```bash
# Ubuntu/Debian
ufw allow 22        # SSH
ufw allow 80        # HTTP
ufw allow 443       # HTTPS
ufw deny 5432       # 不對外開放資料庫
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### 2. SSL/TLS 設定
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 容器安全
```bash
# 使用非 root 使用者
# Dockerfile
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# 限制容器權限
docker run --read-only --tmpfs /tmp --user 1000:1000 mychordhub-backend

# 掃描映像漏洞
docker scan mychordhub-backend:latest
```

## 🚨 故障排除

### 常見問題

#### 1. 容器無法啟動
```bash
# 檢查日誌
docker-compose logs <service-name>

# 檢查映像
docker images

# 重新建置
docker-compose build --no-cache
```

#### 2. 資料庫連線失敗
```bash
# 檢查資料庫狀態
docker-compose exec db pg_isready -U postgres

# 重置資料庫連線
docker-compose restart db

# 檢查網路
docker network ls
docker network inspect mychordhub_mychordhub-network
```

#### 3. 效能問題
```bash
# 檢查資源使用
docker stats

# 檢查磁碟空間
df -h
docker system df

# 清理未使用資源
docker system prune -f
```

#### 4. SSL 憑證問題
```bash
# 檢查憑證有效期
openssl x509 -in nginx/ssl/cert.pem -text -noout

# 測試 SSL
openssl s_client -connect yourdomain.com:443

# 自動更新 Let's Encrypt
certbot renew --dry-run
```

---

需要協助？請查看 [README.md](README.md) 或提交 Issue。