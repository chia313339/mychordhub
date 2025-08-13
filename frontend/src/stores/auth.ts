import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'
import type {
  User,
  LoginCredentials,
  RegisterData,
  UpdateProfileData,
  ChangePasswordData,
} from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const isEmailVerified = computed(() => user.value?.email_verified ?? false)

  // 從 localStorage 恢復登入狀態
  const initializeAuth = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        isLoading.value = true
        user.value = await authService.getCurrentUser()
      } catch (err) {
        // Token 無效，清除本地存儲
        clearAuth()
      } finally {
        isLoading.value = false
      }
    }
  }

  // 清除認證狀態
  const clearAuth = () => {
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    error.value = null
  }

  // Actions
  const login = async (credentials: LoginCredentials) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await authService.login(credentials)

      // 存儲 tokens
      localStorage.setItem('access_token', response.tokens.access_token)
      localStorage.setItem('refresh_token', response.tokens.refresh_token)

      // 設定用戶資訊
      user.value = response.user

      return response
    } catch (err: any) {
      error.value = err.message || '登入失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await authService.register(data)

      // 註冊成功後自動登入
      localStorage.setItem('access_token', response.tokens.access_token)
      localStorage.setItem('refresh_token', response.tokens.refresh_token)

      user.value = response.user

      return response
    } catch (err: any) {
      error.value = err.message || '註冊失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      isLoading.value = true
      await authService.logout()
    } catch (err) {
      console.warn('Logout API call failed:', err)
    } finally {
      clearAuth()
      isLoading.value = false
    }
  }

  const updateProfile = async (data: UpdateProfileData) => {
    try {
      isLoading.value = true
      error.value = null

      const updatedUser = await authService.updateProfile(data)
      user.value = updatedUser

      return updatedUser
    } catch (err: any) {
      error.value = err.message || '更新個人資料失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (data: ChangePasswordData) => {
    try {
      isLoading.value = true
      error.value = null

      await authService.changePassword(data)
    } catch (err: any) {
      error.value = err.message || '修改密碼失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const uploadAvatar = async (file: File) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await authService.uploadAvatar(file)

      if (user.value) {
        user.value.avatar_url = response.avatar_url
      }

      return response
    } catch (err: any) {
      error.value = err.message || '上傳頭像失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const verifyEmail = async (token: string) => {
    try {
      isLoading.value = true
      error.value = null

      await authService.verifyEmail(token)

      // 重新獲取用戶資訊
      if (user.value) {
        user.value = await authService.getCurrentUser()
      }
    } catch (err: any) {
      error.value = err.message || '郵箱驗證失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const resendVerificationEmail = async () => {
    try {
      isLoading.value = true
      error.value = null

      await authService.resendVerificationEmail()
    } catch (err: any) {
      error.value = err.message || '重新發送驗證郵件失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const forgotPassword = async (email: string) => {
    try {
      isLoading.value = true
      error.value = null

      await authService.forgotPassword(email)
    } catch (err: any) {
      error.value = err.message || '發送重設密碼郵件失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const resetPassword = async (token: string, newPassword: string) => {
    try {
      isLoading.value = true
      error.value = null

      await authService.resetPassword(token, newPassword)
    } catch (err: any) {
      error.value = err.message || '重設密碼失敗'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    user,
    isLoading,
    error,

    // Getters
    isAuthenticated,
    isEmailVerified,

    // Actions
    initializeAuth,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    uploadAvatar,
    verifyEmail,
    resendVerificationEmail,
    forgotPassword,
    resetPassword,
    clearError,
  }
})
