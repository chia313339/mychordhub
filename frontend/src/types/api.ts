// API 響應基礎類型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: ApiError
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, string[]>
}

// 分頁相關類型
export interface PaginationParams {
  page?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface PaginationResponse {
  page: number
  size: number
  total: number
  pages: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: PaginationResponse
}

// 搜索相關類型
export interface SearchParams extends PaginationParams {
  query?: string
  filters?: Record<string, any>
}

// HTTP 請求配置
export interface RequestConfig {
  headers?: Record<string, string>
  timeout?: number
  retry?: number
}
