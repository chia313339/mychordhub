// 統一導出所有類型定義
export * from './api'
export * from './user'
export * from './music'

// 應用狀態相關類型
export interface AppState {
  isLoading: boolean
  error: string | null
  theme: 'light' | 'dark'
  language: 'zh' | 'en'
}

// 響應式斷點類型
export interface Breakpoints {
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  screenWidth: number
}

// 通知系統類型
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  actions?: NotificationAction[]
}

export interface NotificationAction {
  label: string
  action: () => void
}

// 表單驗證類型
export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => boolean | string
}

export interface ValidationErrors {
  [key: string]: string[]
}

// 音頻播放相關類型
export interface AudioPlayer {
  isPlaying: boolean
  currentTime: number
  duration: number
  volume: number
  speed: number
}

// 快捷鍵配置類型
export interface KeyboardShortcut {
  key: string
  modifiers?: ('ctrl' | 'shift' | 'alt' | 'meta')[]
  action: () => void
  description: string
}
