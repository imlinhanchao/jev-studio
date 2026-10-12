export interface SummaryStats {
  total_requests: number
  total_tokens: number
  prompt_tokens: number
  decision_tokens: number
  avg_latency_ms: number
  active_keys_count: number
  total_keys_count: number
}

export interface TimeSeriesPoint {
  date: string
  requests: number
  tokens: number
  avg_latency_ms: number
}

export interface DecisionTypeDistribution {
  choice: number
  noul: number
  score: number
}

export interface KeyUsageItem {
  key_id: number
  name: string
  key_prefix: string
  tokens_used: number
  token_limit: number
  percent_used: number
  requests_count: number
  is_active: boolean
}

export interface UsageLogItem {
  id: number
  request_id: string
  key_id?: number | null
  key_name?: string | null
  key_prefix?: string | null
  decision_types: string
  prompt_tokens: number
  decision_tokens: number
  total_tokens: number
  latency_ms: number
  status_code: number
  created_at: string
}

export interface AnalyticsDashboardData {
  summary: SummaryStats
  timeseries: TimeSeriesPoint[]
  type_distribution: DecisionTypeDistribution
  key_usage: KeyUsageItem[]
}
