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
  is_loaded: boolean
}

export interface ModelProgress {
  model_id: string
  state: 'idle' | 'preparing' | 'downloading' | 'loading' | 'ready' | 'error'
  percent: number
  message: string
  updated_at: number
}

export interface ModelStatus {
  model_id: string
  name: string
  architecture: string
  mode: 'real' | 'unloaded' | 'error'
  is_loaded: boolean
  is_loading: boolean
  device: string
  memory_mb: number
  load_error?: string | null
  cache_enabled: boolean
  loaded_models: string[]
  progress: ModelProgress
  supports_modalities: string[]
  decision_primitives: string[]
  available_models: ModelItem[]
}
