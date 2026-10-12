export interface APIKeyItem {
  id: number
  name: string
  key_prefix: string
  is_active: boolean
  token_limit: number
  tokens_used: number
  rate_limit_rpm: number
  created_at: string
  expires_at?: string | null
  last_used_at?: string | null
  percent_used: number
}

export interface KeyCreatePayload {
  name: string
  token_limit: number
  rate_limit_rpm: number
  expires_in_days?: number | null
}

export interface KeyCreatedResponse extends APIKeyItem {
  raw_key: string
}

export interface KeyUpdatePayload {
  name?: string
  is_active?: boolean
  token_limit?: number
  rate_limit_rpm?: number
}
