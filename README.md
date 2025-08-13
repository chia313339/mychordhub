# 🎸 MyChordHub - 線上吉他譜編輯平台

一個功能完整的線上吉他譜編輯和瀏覽平台，支持手機和PC，提供簡單易用的吉他譜編輯體驗。

## ✨ 主要功能

### 🔍 瀏覽模式
- **智能搜索**：根據歌曲名稱、歌手搜索
- **高級篩選**：按調性、難度、風格篩選
- **歌曲瀏覽**：清晰的歌詞和絃顯示
- **自動播放**：可調速度的自動滾動播放

### ✏️ 編輯模式
- **歌詞編輯**：在歌詞中插入和絃標記
- **和絃庫**：內建常用和絃，支持自定義
- **六線譜顯示**：清晰的和絃指法圖示
- **Key/Capo調整**：自動轉調所有和絃

### 🎵 音樂功能
- **調性轉換**：Key和Capo位置調整
- **和絃顯示**：文字模式 ↔ 六線譜模式切換
- **速度控制**：自定義播放滾動速度
- **音頻播放**：和絃音頻預覽（基礎版）

### 📱 用戶體驗
- **響應式設計**：完美適配手機和桌面
- **離開提醒**：編輯時離開頁面會提醒保存
- **實時預覽**：編輯時即時查看效果
- **收藏功能**：個人歌曲收藏管理

## 🏗️ 技術架構

### 三層架構
- **前端**：Vue.js 3 + TypeScript + Vite
- **後端**：FastAPI + SQLAlchemy + PostgreSQL
- **資料庫**：PostgreSQL + Redis

### 容器化部署
- **Docker**：完整的容器化部署
- **docker-compose**：開發環境一鍵啟動
- **多環境支持**：開發/測試/生產環境配置

## 🚀 快速開始

### 前置要求
- Docker Desktop (需要先啟動)
- Git
- Make (macOS/Linux) 或手動執行 docker-compose 命令

### 1. 啟動 Docker Desktop
請確保 Docker Desktop 已安裝並正在運行：
- macOS: 打開 Docker Desktop 應用程式
- Windows: 啟動 Docker Desktop
- Linux: 啟動 Docker daemon

### 2. 克隆專案並啟動
```bash
# 確認已在專案目錄
cd /Users/lee/Downloads/mychordhub

# 一鍵啟動開發環境
make install

# 或手動執行
cp .env.example .env
docker-compose -f docker-compose.dev.yml up --build -d
```

### 3. 訪問應用
- **前端應用**：http://localhost:3000
- **後端API**：http://localhost:8000
- **API文檔**：http://localhost:8000/api/v1/docs
- **pgAdmin**：http://localhost:5050 (admin@mychordhub.com / admin)

## 📋 開發指令

```bash
# 查看所有可用指令
make help

# 啟動開發環境
make dev-up

# 查看服務狀態
make status

# 查看日誌
make dev-logs

# 停止服務
make dev-down

# 重啟服務
make dev-restart

# 進入後端容器
make backend-shell

# 進入前端容器
make frontend-shell

# 執行測試
make test

# 代碼檢查
make lint

# 清理資源
make clean
```

## 🗂️ 專案結構

```
mychordhub/
├── frontend/                 # Vue.js 前端應用
│   ├── src/
│   │   ├── components/       # Vue組件
│   │   │   ├── features/     # 功能組件 (和絃顯示、歌詞編輯器等)
│   │   │   ├── layout/       # 佈局組件
│   │   │   └── ui/           # 基礎UI組件
│   │   ├── pages/            # 頁面組件
│   │   ├── stores/           # Pinia狀態管理
│   │   ├── services/         # API服務
│   │   └── types/            # TypeScript類型定義
│   ├── Dockerfile
│   └── package.json
├── backend/                  # FastAPI 後端應用
│   ├── app/
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── crud/             # 資料庫操作
│   │   ├── models/           # SQLAlchemy模型
│   │   ├── schemas/          # Pydantic模型
│   │   └── services/         # 業務邏輯
│   ├── Dockerfile
│   └── pyproject.toml
├── database/                 # 資料庫配置
│   └── init.sql              # 初始化腳本
├── docker-compose.yml        # Docker編排文件
├── docker-compose.dev.yml    # 開發環境配置
├── docker-compose.prod.yml   # 生產環境配置
├── .env.example              # 環境變數範例
├── Makefile                  # 開發工具指令
└── README.md                 # 說明文件
```

## 🎯 核心功能組件

### 前端組件
- **ChordDisplay**：和絃顯示組件（文字/六線譜切換）
- **LyricsEditor**：歌詞編輯器（插入和絃功能）
- **KeyCapoSelector**：Key和Capo選擇器
- **ChordTransposer**：和絃轉調功能
- **PlaybackControl**：自動播放控制
- **SongCard**：歌曲卡片組件

### 後端API
- **認證系統**：JWT認證、用戶管理
- **歌曲管理**：CRUD操作、搜索、篩選
- **音樂功能**：和絃轉換、調性計算
- **收藏系統**：個人收藏管理
- **評分系統**：歌曲評分功能

## 🔧 環境配置

### 開發環境 (.env)
```bash
# 資料庫配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/mychordhub
REDIS_URL=redis://localhost:6379/0

# JWT設定
JWT_SECRET_KEY=your-development-secret-key

# CORS設定
CORS_ORIGINS=http://localhost:3000

# 前端配置
VITE_API_BASE_URL=http://localhost:8000
```

## 🧪 測試

```bash
# 執行所有測試
make test

# 執行後端測試
make test-backend

# 執行前端測試
make test-frontend

# 後端API演示
cd backend && python demo.py
```

## 📊 資料庫

### 主要資料表
- **users**：用戶資料
- **songs**：歌曲資料（歌詞、和絃、基本信息）
- **custom_chords**：自定義和絃
- **favorites**：收藏關聯
- **ratings**：評分資料

### 範例資料
初始化時會自動建立：
- 示範用戶帳號
- 經典歌曲範例（Amazing Grace、House of the Rising Sun）
- 常用和絃庫（C、G、Am、F、Dm、E等）

## 🚀 部署

### 生產環境
```bash
# 建置生產映像
make prod-build

# 啟動生產環境
make prod-up
```

### 雲端部署
支援部署到：
- Google Cloud Platform
- AWS
- Azure
- 任何支援Docker的平台

## 🛠️ 疑難排解

### Docker 問題
```bash
# 檢查Docker狀態
docker ps

# 重新建置容器
make clean && make install

# 查看容器日誌
make dev-logs
```

### 資料庫問題
```bash
# 重置資料庫
make db-reset

# 進入資料庫
make db-shell

# 備份資料庫
make db-backup
```

## 📚 相關文檔

- [Docker架構文檔](README-Docker.md)
- [API文檔](http://localhost:8000/api/v1/docs) (啟動後端後可訪問)
- [技術架構指南](.ai-rules/)

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 建立 Pull Request

## 📄 授權

此專案採用 MIT 授權條款。

---

**MyChordHub** - 讓吉他學習變得簡單有趣！ 🎸✨