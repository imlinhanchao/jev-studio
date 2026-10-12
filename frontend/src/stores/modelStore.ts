import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ModelStatus } from '@/types/model'
import { fetchModelStatus, selectModel, loadModelWeights, unloadModelWeights } from '@/api/model'

export const useModelStore = defineStore('model', () => {
  const status = ref<ModelStatus | null>(null)
  const loading = ref(false)
  const actionLoading = ref(false)

  const availableModels = computed(() => status.value?.available_models || [])
  const activeModelId = computed(() => status.value?.model_id || 'LiquidAI/d1-omni-600M')
  const activeModelName = computed(() => status.value?.name || 'Liquid AI d1-omni-600M')

  async function loadStatus() {
    loading.value = true
    try {
      status.value = await fetchModelStatus()
    } catch (e) {
      console.error('Failed to load model status:', e)
    } finally {
      loading.value = false
    }
  }

  async function switchModel(modelId: string) {
    actionLoading.value = true
    try {
      status.value = await selectModel(modelId)
    } catch (e) {
      console.error('Failed to switch model:', e)
    } finally {
      actionLoading.value = false
    }
  }

  async function triggerLoadReal(force = false, modelId?: string) {
    actionLoading.value = true
    try {
      await loadModelWeights(force, modelId)
      await loadStatus()
    } finally {
      actionLoading.value = false
    }
  }

  async function triggerUnload() {
    actionLoading.value = true
    try {
      await unloadModelWeights()
      await loadStatus()
    } finally {
      actionLoading.value = false
    }
  }

  return {
    status,
    loading,
    actionLoading,
    availableModels,
    activeModelId,
    activeModelName,
    loadStatus,
    switchModel,
    triggerLoadReal,
    triggerUnload,
  }
})
