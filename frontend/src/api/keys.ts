import { apiClient } from './client'
import type { APIKeyItem, KeyCreatePayload, KeyCreatedResponse, KeyUpdatePayload } from '@/types/key'

export async function fetchKeys(): Promise<APIKeyItem[]> {
  const response = await apiClient.get<APIKeyItem[]>('/keys')
  return response.data
}

export async function createKey(payload: KeyCreatePayload): Promise<KeyCreatedResponse> {
  const response = await apiClient.post<KeyCreatedResponse>('/keys', payload)
  return response.data
}

export async function updateKey(id: number, payload: KeyUpdatePayload): Promise<APIKeyItem> {
  const response = await apiClient.patch<APIKeyItem>(`/keys/${id}`, payload)
  return response.data
}

export async function deleteKey(id: number): Promise<void> {
  await apiClient.delete(`/keys/${id}`)
}
