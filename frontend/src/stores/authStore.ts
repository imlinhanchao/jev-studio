import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { setAuthToken, getAuthToken } from '@/api/client'
import type { UserInfo, LoginRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(getAuthToken())
  const user = ref<UserInfo | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isInitialized = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials: LoginRequest): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const res = await authApi.login(credentials)
      token.value = res.access_token
      user.value = {
        username: res.username,
        role: res.role,
      }
      setAuthToken(res.access_token)
      return true
    } catch (err: any) {
      if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = '登录失败，请检查网络连接或后端服务状态'
      }
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } finally {
      token.value = null
      user.value = null
      error.value = null
      setAuthToken(null)
    }
  }

  async function initAuth(): Promise<boolean> {
    if (isInitialized.value) return isAuthenticated.value
    isInitialized.value = true

    if (!token.value) {
      return false
    }

    try {
      const userInfo = await authApi.getMe()
      user.value = userInfo
      return true
    } catch {
      // Invalid or expired token
      token.value = null
      user.value = null
      setAuthToken(null)
      return false
    }
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    isInitialized,
    login,
    logout,
    initAuth,
  }
})
