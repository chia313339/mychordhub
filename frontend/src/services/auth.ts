import { ApiService } from './api'
import type {
  User,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  UpdateProfileData,
  ChangePasswordData,
} from '@/types'

export class AuthService extends ApiService {
  /**
   * 用戶註冊
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    return this.post<AuthResponse>('/auth/register', data)
  }

  /**
   * 用戶登入
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    return this.post<AuthResponse>('/auth/login', credentials)
  }

  /**
   * 用戶登出
   */
  async logout(): Promise<void> {
    return this.post<void>('/auth/logout')
  }

  /**
   * 刷新訪問令牌
   */
  async refreshToken(refreshToken: string): Promise<{ access_token: string; expires_in: number }> {
    return this.post<{ access_token: string; expires_in: number }>('/auth/refresh', {
      refresh_token: refreshToken,
    })
  }

  /**
   * 驗證電子郵件
   */
  async verifyEmail(token: string): Promise<void> {
    return this.post<void>('/auth/verify-email', { token })
  }

  /**
   * 重新發送驗證郵件
   */
  async resendVerificationEmail(): Promise<void> {
    return this.post<void>('/auth/resend-verification')
  }

  /**
   * 忘記密碼
   */
  async forgotPassword(email: string): Promise<void> {
    return this.post<void>('/auth/forgot-password', { email })
  }

  /**
   * 重設密碼
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    return this.post<void>('/auth/reset-password', {
      token,
      new_password: newPassword,
    })
  }

  /**
   * 獲取當前用戶資料
   */
  async getCurrentUser(): Promise<User> {
    return this.get<User>('/auth/me')
  }

  /**
   * 更新用戶資料
   */
  async updateProfile(data: UpdateProfileData): Promise<User> {
    return this.put<User>('/auth/profile', data)
  }

  /**
   * 修改密碼
   */
  async changePassword(data: ChangePasswordData): Promise<void> {
    return this.put<void>('/auth/change-password', data)
  }

  /**
   * 上傳頭像
   */
  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData()
    formData.append('avatar', file)

    return this.post<{ avatar_url: string }>('/auth/upload-avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  }

  /**
   * 刪除帳戶
   */
  async deleteAccount(password: string): Promise<void> {
    return this.delete<void>('/auth/account', {
      data: { password },
    })
  }
}

// 創建單例實例
export const authService = new AuthService()
