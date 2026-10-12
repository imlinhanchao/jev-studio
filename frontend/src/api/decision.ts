import { apiClient } from './client'
import type { DecisionRequest, DecisionResponse, DecisionTemplate } from '@/types/decision'

export async function predictDecision(
  payload: DecisionRequest,
  apiKey?: string
): Promise<DecisionResponse> {
  const headers: Record<string, string> = {}
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`
  }
  const response = await apiClient.post<DecisionResponse>('/decision/predict', payload, { headers })
  return response.data
}

export async function fetchTemplates(): Promise<DecisionTemplate[]> {
  const response = await apiClient.get<DecisionTemplate[]>('/decision/templates')
  return response.data
}
