import { apiClient } from './client'
import type { ModelStatus, ModelItem, ModelProgress } from '@/types/model'

export async function fetchModelStatus(): Promise<ModelStatus> {
  const response = await apiClient.get<ModelStatus>('/model/status')
  return response.data
}

export async function fetchModelProgress(): Promise<ModelProgress> {
  const response = await apiClient.get<ModelProgress>('/model/progress')
  return response.data
}

export async function fetchModelList(): Promise<ModelItem[]> {
  const response = await apiClient.get<ModelItem[]>('/model/list')
  return response.data
}

export async function selectModel(modelId: string): Promise<ModelStatus> {
  const response = await apiClient.post<ModelStatus>('/model/select', { model_id: modelId })
  return response.data
}

export async function setCacheMode(enabled: boolean): Promise<ModelStatus> {
  const response = await apiClient.post<ModelStatus>('/model/cache-mode', { enabled })
  return response.data
}

export async function loadModelWeights(force = false, modelId?: string): Promise<any> {
  const response = await apiClient.post('/model/load', null, {
    params: { force, model_id: modelId },
  })
  return response.data
}

export async function unloadModelWeights(modelId?: string): Promise<any> {
  const response = await apiClient.post('/model/unload', null, {
    params: { model_id: modelId },
  })
  return response.data
}
