// 用戶相關類型定義
export interface User {
  id: string
  email: string
  display_name: string
  bio?: string
  avatar_url?: string
  email_verified: boolean
  created_at: string
  updated_at: string
}

// 認證相關類型
export interface LoginCredentials {
  email: string
  password: string
  remember_me?: boolean
}

export interface RegisterData {
  email: string
  password: string
  confirm_password: string
  display_name: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthResponse {
  user: User
  tokens: AuthTokens
}

// 用戶資料更新
export interface UpdateProfileData {
  display_name?: string
  bio?: string
  avatar_url?: string
}

export interface ChangePasswordData {
  current_password: string
  new_password: string
  confirm_password: string
}

// 收藏夾類型
export interface Collection {
  id: string
  user_id: string
  name: string
  description?: string
  is_default: boolean
  created_at: string
  song_count?: number
}

export interface CreateCollectionData {
  name: string
  description?: string
}
