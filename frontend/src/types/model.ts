export interface ModelItem {
  id: string
  name: string
  provider: string
  architecture: string
  parameters: string
  description: string
  tags: string[]
  recommended_for: string
  typical_latency_ms: string
  is_active: boolean
}

export interface ModelStatus {
  model_id: string
  name: string
  architecture: string
  mode: 'real' | 'simulation'
  is_loaded: boolean
  is_loading: boolean
  device: string
  memory_mb: number
  load_error?: string | null
  supports_modalities: string[]
  decision_primitives: string[]
  available_models: ModelItem[]
}
