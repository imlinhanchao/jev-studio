import { apiClient } from './client'
import type { LoginRequest, TokenResponse, UserInfo } from '@/types/auth'

export const authApi = {
  async login(payload: LoginRequest): Promise<TokenResponse> {
    const res = await apiClient.post<TokenResponse>('/auth/login', payload)
    return res.data
  },

  async getMe(): Promise<UserInfo> {
    const res = await apiClient.get<UserInfo>('/auth/me')
    return res.data
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // Ignore network logout errors
    }
  },
}
