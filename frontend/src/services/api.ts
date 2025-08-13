import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { ApiResponse, ApiError } from '@/types'

// API 基礎配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// 創建 Axios 實例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加認證 token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加請求時間戳（用於緩存控制）
    config.params = {
      ...config.params,
      _t: Date.now(),
    }

    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  },
)

// 響應攔截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response
  },
  async (error) => {
    const { response, config } = error

    // Token 過期處理
    if (response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken && !config._retry) {
        config._retry = true

        try {
          const refreshResponse = await apiClient.post('/auth/refresh', {
            refresh_token: refreshToken,
          })

          const { access_token } = refreshResponse.data.data
          localStorage.setItem('access_token', access_token)

          // 重新發送原請求
          config.headers.Authorization = `Bearer ${access_token}`
          return apiClient(config)
        } catch (refreshError) {
          // Refresh 失敗，清除本地存儲並重導向登入
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/auth/login'
          return Promise.reject(refreshError)
        }
      } else {
        // 沒有 refresh token 或重試失敗
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/auth/login'
      }
    }

    // 網路錯誤處理
    if (!response) {
      console.error('Network error:', error.message)
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: '網路連線失敗，請檢查您的網路連線',
      })
    }

    // 伺服器錯誤處理
    const apiError: ApiError = {
      code: response.data?.error?.code || 'UNKNOWN_ERROR',
      message: response.data?.error?.message || '伺服器錯誤',
      details: response.data?.error?.details,
    }

    console.error('API error:', apiError)
    return Promise.reject(apiError)
  },
)

// API 服務基類
export class ApiService {
  protected client = apiClient

  // GET 請求
  protected async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<ApiResponse<T>>(url, config)
    return response.data.data as T
  }

  // POST 請求
  protected async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, data, config)
    return response.data.data as T
  }

  // PUT 請求
  protected async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<ApiResponse<T>>(url, data, config)
    return response.data.data as T
  }

  // DELETE 請求
  protected async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<ApiResponse<T>>(url, config)
    return response.data.data as T
  }

  // PATCH 請求
  protected async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<ApiResponse<T>>(url, data, config)
    return response.data.data as T
  }
}

export default apiClient
