# MyChordHub Docker 架構文件

## 🏗️ 架構概覽

MyChordHub 採用三層式 Docker 架構，包含：

- **前端**: Vue.js + TypeScript + Vite
- **後端**: FastAPI + Python + SQLAlchemy  
- **資料庫**: PostgreSQL + Redis

## 📁 目錄結構

```
mychordhub/
├── frontend/                 # Vue.js 前端應用
│   ├── Dockerfile           # 前端容器配置
│   └── nginx.conf           # 生產環境 Nginx 配置
├── backend/                 # FastAPI 後端應用
│   └── Dockerfile           # 後端容器配置
├── database/               # 資料庫配置
│   └── init.sql            # 資料庫初始化腳本
├── docker-compose.yml      # 預設 Docker Compose 配置
├── docker-compose.dev.yml  # 開發環境配置
├── docker-compose.prod.yml # 生產環境配置
├── .env.example           # 環境變數範例
└── Makefile              # 開發工具命令集
```

## 🚀 快速開始

### 1. 環境準備

```bash
# 確保已安裝 Docker 和 Docker Compose
docker --version
docker-compose --version

# 複製環境變數檔案
cp .env.example .env
```

### 2. 一鍵啟動開發環境

```bash
# 使用 Makefile (推薦)
make install

# 或手動執行
docker-compose -f docker-compose.dev.yml up --build -d
```

### 3. 訪問應用

- **前端**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文件**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

## 🛠️ 開發工具

### Makefile 命令

```bash
make help              # 顯示所有可用命令
make dev-up           # 啟動開發環境
make dev-down         # 停止開發環境  
make dev-logs         # 顯示日誌
make test             # 執行測試
make lint             # 代碼檢查
make clean            # 清理資源
```

### 開發環境管理

```bash
# 啟動服務
make dev-up

# 查看服務狀態
make status

# 查看日誌
make dev-logs
make logs-backend     # 只看後端日誌
make logs-frontend    # 只看前端日誌

# 重啟服務
make dev-restart

# 停止服務
make dev-down
```

### 資料庫管理

```bash
# 進入資料庫命令列
make db-shell

# 重置資料庫
make db-reset

# 備份資料庫
make db-backup
```

### 容器管理

```bash
# 進入後端容器
make backend-shell

# 進入前端容器  
make frontend-shell

# 查看容器狀態
docker-compose -f docker-compose.dev.yml ps
```

## 🌍 環境配置

### 開發環境 (docker-compose.dev.yml)

- 啟用熱重載
- 掛載本地代碼
- 包含開發工具 (pgAdmin)
- 詳細日誌輸出

### 生產環境 (docker-compose.prod.yml)

- 多階段構建優化
- 資源限制設定
- SSL 支援
- 負載均衡配置

### 環境變數

在 `.env` 檔案中配置：

```bash
# 基本設定
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:password@db:5432/mychordhub
REDIS_URL=redis://redis:6379/0

# 安全設定
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000

# 功能設定
ENABLE_AUDIO_SYNTHESIS=true
LOG_LEVEL=DEBUG
```

## 🔧 容器配置詳解

### 前端容器 (frontend/)

**Dockerfile 特色**：
- 多階段構建 (開發/生產)
- Node.js 18 Alpine 基礎映像
- Vite 開發伺服器配置
- Nginx 生產環境設定

**開發模式**：
```dockerfile
# 熱重載支援
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**生產模式**：
```dockerfile
# 靜態檔案服務
FROM nginx:alpine as production
COPY --from=build /app/dist /usr/share/nginx/html
```

### 後端容器 (backend/)

**Dockerfile 特色**：
- Python 3.11 Slim 基礎映像
- Poetry 套件管理
- 非 root 使用者運行
- 健康檢查配置

**安全設定**：
```dockerfile
# 建立非 root 使用者
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

**效能優化**：
```dockerfile
# Poetry 快取設定
ENV POETRY_CACHE_DIR=/tmp/poetry_cache
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR
```

### 資料庫配置 (database/)

**PostgreSQL 設定**：
- 自動初始化腳本
- 健康檢查
- 資料持久化
- 索引優化

**Redis 設定**：
- 記憶體限制
- AOF 持久化
- LRU 清除策略

## 📊 監控與日誌

### 健康檢查

所有服務都配置了健康檢查：

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### 日誌管理

```bash
# 即時查看所有日誌
make dev-logs

# 查看特定服務日誌
docker-compose -f docker-compose.dev.yml logs -f backend

# 查看最近日誌
docker-compose -f docker-compose.dev.yml logs --tail=100 frontend
```

## 🔒 安全考量

### 開發環境
- 固定的開發用密碼
- CORS 寬鬆設定
- 詳細錯誤訊息

### 生產環境
- 環境變數注入敏感資訊
- 嚴格的 CORS 設定
- 最小權限原則
- SSL 終端配置

## 🚢 部署指南

### 本地生產環境測試

```bash
# 建置生產映像
make prod-build

# 啟動生產環境
make prod-up

# 監控狀態
docker-compose -f docker-compose.prod.yml ps
```

### 雲端部署準備

1. **環境變數設定**：設定生產環境變數
2. **SSL 憑證**：配置 HTTPS 憑證
3. **資料庫遷移**：執行生產資料庫初始化
4. **監控設定**：配置日誌收集和監控

## 🔧 疑難排解

### 常見問題

**容器無法啟動**：
```bash
# 檢查容器日誌
make dev-logs

# 檢查網路狀態
docker network ls
```

**資料庫連線失敗**：
```bash
# 檢查資料庫健康狀態
docker-compose -f docker-compose.dev.yml ps db

# 手動測試連線
make db-shell
```

**前端無法連接後端**：
```bash
# 檢查 CORS 設定
echo $CORS_ORIGINS

# 檢查網路連通性
docker-compose -f docker-compose.dev.yml exec frontend ping backend
```

### 清理和重建

```bash
# 完全清理重建
make clean-all
make install
```

## 📈 效能調校

### 資源配置

```yaml
# 生產環境資源限制
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

### 快取策略

- Redis 記憶體快取
- Nginx 靜態檔案快取
- 瀏覽器快取標頭

---

更多技術細節請參考 `.ai-rules/` 目錄下的架構文件。