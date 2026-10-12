import { apiClient } from './client'
import type { AnalyticsDashboardData, UsageLogItem } from '@/types/analytics'

export async function fetchDashboardData(): Promise<AnalyticsDashboardData> {
  const response = await apiClient.get<AnalyticsDashboardData>('/analytics/dashboard')
  return response.data
}

export async function fetchUsageLogs(skip = 0, limit = 50, keyId?: number): Promise<UsageLogItem[]> {
  const params: Record<string, any> = { skip, limit }
  if (keyId !== undefined) {
    params.key_id = keyId
  }
  const response = await apiClient.get<UsageLogItem[]>('/analytics/logs', { params })
  return response.data
}
