---
title: 專案結構規範
description: "MyChordHub 專案的目錄組織、命名規則及開發流程指引。"
inclusion: always
---

# MyChordHub 專案結構規範

## 根目錄結構
```
mychordhub/
├── .ai-rules/              # AI 指導文件
├── frontend/               # 前端應用
├── backend/                # 後端 API
├── database/               # 資料庫相關文件
├── docker/                 # Docker 配置文件
├── docs/                   # 專案文檔
├── scripts/                # 自動化腳本
├── .github/                # GitHub Actions 工作流
├── docker-compose.yml      # 多服務編排
├── docker-compose.dev.yml  # 開發環境配置
├── README.md               # 專案說明
└── package.json            # 根項目配置
```

## 前端結構詳細規範

### 目錄組織
```
frontend/
├── public/                 # 靜態資源
│   ├── icons/             # 圖標文件
│   ├── images/            # 圖片資源
│   └── manifest.json      # PWA 配置
├── src/
│   ├── components/        # 可重用組件
│   │   ├── ui/           # 基礎 UI 組件
│   │   ├── features/     # 功能型組件
│   │   └── layout/       # 佈局組件
│   ├── pages/            # 頁面組件
│   │   ├── Browse/       # 瀏覽頁面
│   │   ├── Edit/         # 編輯頁面
│   │   ├── Profile/      # 用戶頁面
│   │   └── Auth/         # 認證頁面
│   ├── hooks/            # 自定義 React Hooks
│   │   ├── useAuth.ts    # 認證相關
│   │   ├── useChord.ts   # 和絃處理
│   │   └── useMusic.ts   # 音樂理論
│   ├── stores/           # 狀態管理
│   │   ├── authStore.ts  # 認證狀態
│   │   ├── editorStore.ts# 編輯器狀態
│   │   └── musicStore.ts # 音樂相關狀態
│   ├── services/         # API 服務
│   │   ├── api.ts        # API 基礎配置
│   │   ├── auth.ts       # 認證服務
│   │   ├── songs.ts      # 歌曲相關
│   │   └── chords.ts     # 和絃相關
│   ├── utils/            # 工具函數
│   │   ├── music/        # 音樂理論工具
│   │   ├── format/       # 格式化工具
│   │   └── validation/   # 驗證函數
│   ├── types/            # TypeScript 類型定義
│   │   ├── api.ts        # API 響應類型
│   │   ├── music.ts      # 音樂相關類型
│   │   └── user.ts       # 用戶相關類型
│   ├── styles/           # 全局樣式
│   │   ├── globals.css   # 全局樣式
│   │   └── components.css# 組件樣式
│   ├── App.tsx           # 根組件
│   ├── main.tsx          # 應用入口
│   └── vite-env.d.ts     # Vite 類型聲明
├── tests/                # 測試文件
│   ├── __mocks__/        # Mock 文件
│   ├── components/       # 組件測試
│   └── utils/            # 工具函數測試
├── .env.example          # 環境變數範例
├── package.json          # 依賴配置
├── tsconfig.json         # TypeScript 配置
├── vite.config.ts        # Vite 配置
└── tailwind.config.js    # Tailwind 配置
```

## 後端結構詳細規範

### 目錄組織
```
backend/
├── src/
│   ├── controllers/      # 路由控制器
│   │   ├── auth.ts       # 認證控制器
│   │   ├── songs.ts      # 歌曲控制器
│   │   ├── chords.ts     # 和絃控制器
│   │   └── users.ts      # 用戶控制器
│   ├── services/         # 業務邏輯層
│   │   ├── authService.ts# 認證服務
│   │   ├── songService.ts# 歌曲服務
│   │   ├── chordService.ts# 和絃服務
│   │   └── musicService.ts# 音樂理論服務
│   ├── models/           # 資料模型
│   │   ├── User.ts       # 用戶模型
│   │   ├── Song.ts       # 歌曲模型
│   │   └── Chord.ts      # 和絃模型
│   ├── middleware/       # 中間件
│   │   ├── auth.ts       # 認證中間件
│   │   ├── validation.ts # 驗證中間件
│   │   └── error.ts      # 錯誤處理
│   ├── routes/           # 路由定義
│   │   ├── auth.ts       # 認證路由
│   │   ├── songs.ts      # 歌曲路由
│   │   └── chords.ts     # 和絃路由
│   ├── utils/            # 工具函數
│   │   ├── music/        # 音樂理論工具
│   │   ├── encryption.ts # 加密工具
│   │   └── logger.ts     # 日誌工具
│   ├── types/            # TypeScript 類型
│   │   ├── api.ts        # API 類型
│   │   ├── database.ts   # 資料庫類型
│   │   └── music.ts      # 音樂類型
│   ├── config/           # 配置文件
│   │   ├── database.ts   # 資料庫配置
│   │   ├── redis.ts      # Redis 配置
│   │   └── app.ts        # 應用配置
│   ├── app.ts            # Express 應用設定
│   └── server.ts         # 伺服器入口
├── prisma/               # Prisma ORM
│   ├── schema.prisma     # 資料庫模式
│   ├── migrations/       # 資料庫遷移
│   └── seed.ts           # 初始數據
├── tests/                # 測試文件
│   ├── integration/      # 整合測試
│   ├── unit/             # 單元測試
│   └── fixtures/         # 測試數據
├── .env.example          # 環境變數範例
├── package.json          # 依賴配置
├── tsconfig.json         # TypeScript 配置
└── jest.config.js        # Jest 測試配置
```

## 命名規則

### 文件命名
- **組件文件**：PascalCase（如 `ChordEditor.tsx`）
- **Hook 文件**：camelCase，以 `use` 開頭（如 `useAuth.ts`）
- **工具函數**：camelCase（如 `musicUtils.ts`）
- **類型定義**：camelCase，以 `types` 結尾（如 `apiTypes.ts`）
- **配置文件**：kebab-case（如 `vite.config.ts`）

### 組件命名
- **React 組件**：PascalCase（如 `ChordEditor`）
- **自定義 Hook**：camelCase，以 `use` 開頭（如 `useChordEditor`）
- **常數**：UPPER_SNAKE_CASE（如 `API_BASE_URL`）

### 資料庫命名
- **表名**：snake_case 複數形式（如 `chord_sheets`）
- **欄位名**：snake_case（如 `created_at`）
- **索引名**：`idx_table_column` 格式

## 開發流程規範

### Git 工作流
```
main
├── develop              # 開發分支
├── feature/chord-editor # 功能分支
├── hotfix/security-fix  # 熱修復分支
└── release/v1.0.0      # 發布分支
```

### 分支命名規則
- **功能分支**：`feature/feature-name`
- **修復分支**：`bugfix/bug-description`
- **熱修復分支**：`hotfix/issue-description`
- **發布分支**：`release/version-number`

### 提交訊息規範
```
type(scope): description

[optional body]

[optional footer]
```

類型：
- `feat`：新功能
- `fix`：錯誤修復
- `docs`：文檔更新
- `style`：代碼格式
- `refactor`：重構
- `test`：測試相關
- `chore`：維護任務

範例：
```
feat(editor): add chord auto-complete functionality

Implement auto-complete for chord input in the editor.
Includes chord suggestions based on current key signature.

Closes #123
```

## 代碼風格指南

### TypeScript 規範
- 使用 `interface` 定義對象類型
- 使用 `type` 定義聯合類型或複雜類型
- 避免使用 `any`，優先使用 `unknown`
- 函數參數和返回值必須有明確類型

### React 組件規範
- 函數組件優於類組件
- 使用 TypeScript interface 定義 props
- 組件內部邏輯使用自定義 hooks 抽取
- 避免在 JSX 中使用複雜邏輯

### CSS 規範
- 優先使用 Tailwind CSS 類別
- 自定義樣式使用 CSS modules 或 styled-components
- 響應式設計採用 mobile-first 原則
- 使用語義化的類名

## 性能優化指引

### 前端優化
- 使用 React.memo 優化組件渲染
- 實施代碼分割和懶加載
- 圖片使用 WebP 格式並添加 lazy loading
- 使用 Web Workers 處理複雜計算

### 後端優化
- 實施適當的資料庫索引
- 使用 Redis 緩存頻繁查詢
- API 響應使用 gzip 壓縮
- 實施連接池管理

## 安全考量

### 前端安全
- 驗證所有用戶輸入
- 使用 HTTPS 傳輸
- 實施 Content Security Policy
- 避免在客戶端存儲敏感數據

### 後端安全
- 使用 HTTPS 和安全 headers
- 實施速率限制
- 輸入驗證和 SQL 注入防護
- 定期更新依賴包