import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ModelProgress, ModelStatus } from '@/types/model'
import {
  fetchModelStatus,
  fetchModelProgress,
  selectModel,
  setCacheMode as apiSetCacheMode,
  loadModelWeights,
  unloadModelWeights,
} from '@/api/model'

const IDLE_PROGRESS: ModelProgress = { model_id: '', state: 'idle', percent: 0, message: '', updated_at: 0 }

export const useModelStore = defineStore('model', () => {
  const status = ref<ModelStatus | null>(null)
  const loading = ref(false)
  const actionLoading = ref(false)
  const progress = ref<ModelProgress>({ ...IDLE_PROGRESS })

  const availableModels = computed(() => status.value?.available_models || [])
  const activeModelId = computed(() => status.value?.model_id || 'LiquidAI/d1-omni-600M')
  const activeModelName = computed(() => status.value?.name || 'Liquid AI d1-omni-600M')
  const cacheEnabled = computed(() => status.value?.cache_enabled ?? false)
  const loadedModels = computed(() => status.value?.loaded_models || [])

  const isBusy = computed(() => {
    const s = progress.value.state
    return actionLoading.value || s === 'preparing' || s === 'downloading' || s === 'loading'
  })

  let pollTimer: ReturnType<typeof setInterval> | null = null

  function startProgressPolling() {
    stopProgressPolling()
    pollTimer = setInterval(async () => {
      try {
        progress.value = await fetchModelProgress()
      } catch (e) {
        /* ignore transient polling errors */
      }
    }, 600)
  }

  function stopProgressPolling() {
    if (pollTimer !== null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  async function loadStatus() {
    loading.value = true
    try {
      status.value = await fetchModelStatus()
      progress.value = status.value.progress
    } catch (e) {
      console.error('Failed to load model status:', e)
    } finally {
      loading.value = false
    }
  }

  function beginProgress(message: string) {
    progress.value = { ...progress.value, state: 'preparing', percent: 0, message, updated_at: Date.now() / 1000 }
  }

  async function switchModel(modelId: string) {
    actionLoading.value = true
    beginProgress(`准备切换至 ${modelId} ...`)
    startProgressPolling()
    try {
      status.value = await selectModel(modelId)
    } catch (e) {
      console.error('Failed to switch model:', e)
    } finally {
      stopProgressPolling()
      await loadStatus()
      actionLoading.value = false
    }
  }

  async function triggerLoadReal(force = false, modelId?: string) {
    actionLoading.value = true
    beginProgress('准备加载权重 ...')
    startProgressPolling()
    try {
      await loadModelWeights(force, modelId)
    } finally {
      stopProgressPolling()
      await loadStatus()
      actionLoading.value = false
    }
  }

  async function triggerUnload(modelId?: string) {
    actionLoading.value = true
    try {
      await unloadModelWeights(modelId)
      await loadStatus()
    } finally {
      actionLoading.value = false
    }
  }

  async function updateCacheMode(enabled: boolean) {
    actionLoading.value = true
    try {
      status.value = await apiSetCacheMode(enabled)
    } catch (e) {
      console.error('Failed to set cache mode:', e)
    } finally {
      actionLoading.value = false
    }
  }

  return {
    status,
    loading,
    actionLoading,
    progress,
    availableModels,
    activeModelId,
    activeModelName,
    cacheEnabled,
    loadedModels,
    isBusy,
    loadStatus,
    switchModel,
    triggerLoadReal,
    triggerUnload,
    updateCacheMode,
  }
})
