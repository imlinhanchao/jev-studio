export type QuestionType = 'choice' | 'noul' | 'score'

export interface QuestionDefinition {
  type: QuestionType
  instructions: string
  criteria?: Record<string, string> | string
  scale?: number
}

export interface DecisionRequest {
  input: string
  image?: string
  questions: Record<string, QuestionDefinition>
  model?: string
  metadata?: Record<string, any>
}

export interface ChoiceResult {
  choice: string
  probabilities: Record<string, number>
  confidence: number
}

export interface NoulResult {
  decision: boolean
  probability: number
}

export interface ScoreResult {
  score: number
  scale: number
  confidence: number
}

export interface UsageInfo {
  prompt_tokens: number
  decision_tokens: number
  total_tokens: number
}

export interface DecisionResponse {
  id: string
  model: string
  engine: string
  answers: Record<string, ChoiceResult | NoulResult | ScoreResult | any>
  usage: UsageInfo
  latency_ms: number
  created_at: string
}

export interface DecisionTemplate {
  id: string
  name: string
  category: string
  description: string
  sample_input: string
  sample_image?: string
  questions: Record<string, QuestionDefinition>
}
