import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AnalyticsDashboardData, UsageLogItem } from '@/types/analytics'
import { fetchDashboardData, fetchUsageLogs } from '@/api/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
  const dashboard = ref<AnalyticsDashboardData | null>(null)
  const logs = ref<UsageLogItem[]>([])
  const loading = ref(false)
  const logsLoading = ref(false)

  async function loadDashboard() {
    loading.value = true
    try {
      dashboard.value = await fetchDashboardData()
    } catch (e) {
      console.error('Failed to load dashboard metrics:', e)
    } finally {
      loading.value = false
    }
  }

  async function loadLogs(skip = 0, limit = 50, keyId?: number) {
    logsLoading.value = true
    try {
      logs.value = await fetchUsageLogs(skip, limit, keyId)
    } catch (e) {
      console.error('Failed to load logs:', e)
    } finally {
      logsLoading.value = false
    }
  }

  return {
    dashboard,
    logs,
    loading,
    logsLoading,
    loadDashboard,
    loadLogs,
  }
})
