---
title: 技術棧指導
description: "MyChordHub 專案的技術選擇、開發工具及部署架構指引。"
inclusion: always
---

# MyChordHub 技術棧指導

## 架構概覽
採用 Docker 三層架構：前端 + 後端 API + 資料庫

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │  Database   │
│   (React)   │◄──►│  (Node.js)  │◄──►│(PostgreSQL) │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 前端技術棧

### 核心框架
- **React 18+**：現代化組件開發
- **TypeScript**：類型安全，提升開發體驗
- **Vite**：快速開發與構建工具

### UI 框架與樣式
- **Tailwind CSS**：原子化 CSS 框架，快速響應式開發
- **Headless UI** 或 **Radix UI**：無樣式組件庫
- **Framer Motion**：動畫效果（滾動播放功能）

### 狀態管理
- **Zustand**：輕量級狀態管理（推薦）
- **TanStack Query**：服務端狀態管理與緩存

### 音樂相關庫
- **Tone.js**：音頻處理與播放
- **VexFlow**：五線譜/六線譜渲染
- **music-theory**：音樂理論計算（和絃、調性）

## 後端技術棧

### 核心框架
- **Node.js**：JavaScript 運行環境
- **Express.js** 或 **Fastify**：Web 框架
- **TypeScript**：統一前後端語言

### 資料庫
- **PostgreSQL**：主要資料庫，支援 JSON 字段
- **Redis**：緩存與 Session 管理
- **Prisma**：ORM 工具，類型安全的資料庫操作

### 認證與安全
- **JWT**：無狀態認證
- **bcrypt**：密碼加密
- **helmet**：安全中間件
- **cors**：跨域請求處理

### API 設計
- **RESTful API**：標準化接口設計
- **OpenAPI/Swagger**：API 文檔自動生成
- **Zod**：請求驗證與類型推斷

## 開發工具

### 代碼品質
- **ESLint**：代碼風格檢查
- **Prettier**：代碼格式化
- **Husky**：Git hooks 管理
- **lint-staged**：暫存文件檢查

### 測試
- **Vitest**：單元測試框架
- **Testing Library**：React 組件測試
- **Playwright**：端到端測試

### 部署與 DevOps
- **Docker**：容器化部署
- **Docker Compose**：多服務編排
- **GitHub Actions**：CI/CD 流水線

## 檔案結構規範

### 前端結構
```
frontend/
├── src/
│   ├── components/     # 共用組件
│   ├── pages/         # 頁面組件
│   ├── hooks/         # 自定義 hooks
│   ├── stores/        # 狀態管理
│   ├── services/      # API 調用
│   ├── utils/         # 工具函數
│   ├── types/         # TypeScript 類型定義
│   └── styles/        # 全局樣式
├── public/            # 靜態資源
└── tests/            # 測試文件
```

### 後端結構
```
backend/
├── src/
│   ├── controllers/   # 路由控制器
│   ├── services/      # 業務邏輯
│   ├── models/        # 資料模型
│   ├── middleware/    # 中間件
│   ├── utils/         # 工具函數
│   ├── types/         # TypeScript 類型
│   └── config/        # 配置文件
├── prisma/           # 資料庫 schema
└── tests/           # 測試文件
```

## 環境配置

### 開發環境
- Node.js 18+
- pnpm 或 npm 包管理器
- Docker Desktop
- VS Code + 推薦擴展

### 生產環境
- 容器化部署
- 環境變數配置
- SSL 憑證
- 監控與日誌系統

## 性能優化

### 前端優化
- 代碼分割 (Code Splitting)
- 懶加載 (Lazy Loading)
- 圖片優化
- PWA 支援

### 後端優化
- 資料庫索引優化
- Redis 緩存策略
- API 響應壓縮
- 連接池管理

## 音樂相關技術考量

### 和絃處理
- 和絃解析與轉換算法
- 調性轉換邏輯
- Capo 移調計算

### 六線譜渲染
- SVG 或 Canvas 渲染
- 響應式適配
- 列印友好格式

### 自動播放
- 滾動同步算法
- 速度控制
- 暫停/繼續功能