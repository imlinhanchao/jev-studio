import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
})

// Admin Auth Token management
let currentAuthToken: string | null = typeof window !== 'undefined' ? localStorage.getItem('jev_admin_token') : null

export function setAuthToken(token: string | null) {
  currentAuthToken = token
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('jev_admin_token', token)
    } else {
      localStorage.removeItem('jev_admin_token')
    }
  }
}

export function getAuthToken(): string | null {
  return currentAuthToken
}

// Optional API Key injector for Studio / Playground
let currentApiKey: string | null = null

export function setClientApiKey(key: string | null) {
  currentApiKey = key
}

apiClient.interceptors.request.use((config) => {
  if (currentAuthToken) {
    config.headers.Authorization = `Bearer ${currentAuthToken}`
  } else if (currentApiKey) {
    config.headers.Authorization = `Bearer ${currentApiKey}`
  }

  if (currentApiKey) {
    config.headers['x-api-key'] = currentApiKey
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response &&
      error.response.status === 401 &&
      typeof window !== 'undefined' &&
      !error.config?.url?.includes('/auth/login')
    ) {
      setAuthToken(null)
      if (window.location.pathname !== '/login') {
        const currentPath = window.location.pathname + window.location.search
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
      }
    }
    return Promise.reject(error)
  }
)
