import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DecisionRequest, DecisionResponse, DecisionTemplate, QuestionDefinition } from '@/types/decision'
import { fetchTemplates, predictDecision } from '@/api/decision'

export interface ModelOption {
  id: string
  shortName: string
  fullName: string
  tag: string
  architecture: string
  latency: string
  provider: string
}

export const SUPPORTED_DECISION_MODELS: ModelOption[] = [
  {
    id: 'LiquidAI/d1-omni-600M',
    shortName: 'd1-omni-600M',
    fullName: 'Liquid AI d1-omni-600M',
    tag: '600M LFM',
    architecture: 'LFM2.5-Encoder-350M',
    latency: '15-35 ms',
    provider: 'Liquid AI',
  },
  {
    id: 'MiniCPM5-2B-Jev',
    shortName: 'MiniCPM5-2B-Jev',
    fullName: 'MiniCPM5-2B-Jev',
    tag: '2.4B Jev',
    architecture: 'MiniCPM-5-2B-Decision',
    latency: '30-65 ms',
    provider: 'OpenBMB',
  },
]

export const useDecisionStore = defineStore('decision', () => {
  const templates = ref<DecisionTemplate[]>([])
  const selectedTemplateId = ref<string>('')
  
  const inputText = ref<string>('')
  const questions = ref<Record<string, QuestionDefinition>>({})
  const selectedModelId = ref<string>('LiquidAI/d1-omni-600M')
  const modelOptions = ref<ModelOption[]>(SUPPORTED_DECISION_MODELS)

  const currentModelMeta = computed(() => {
    return modelOptions.value.find(m => m.id === selectedModelId.value) || modelOptions.value[0]
  })

  const currentModelShortName = computed(() => {
    return currentModelMeta.value.shortName
  })

  function selectModel(modelId: string) {
    selectedModelId.value = modelId
  }
  
  const currentResponse = ref<DecisionResponse | null>(null)
  const executing = ref(false)
  const error = ref<string | null>(null)

  async function loadTemplates() {
    try {
      templates.value = await fetchTemplates()
      if (templates.value.length > 0 && !selectedTemplateId.value) {
        applyTemplate(templates.value[0])
      }
    } catch (e) {
      console.error('Failed to load templates:', e)
    }
  }

  function applyTemplate(tpl: DecisionTemplate) {
    selectedTemplateId.value = tpl.id
    inputText.value = tpl.sample_input
    // Deep clone questions
    questions.value = JSON.parse(JSON.stringify(tpl.questions))
    currentResponse.value = null
    error.value = null
  }

  function addQuestion(key: string, q: QuestionDefinition) {
    questions.value[key] = q
  }

  function updateQuestion(key: string, q: QuestionDefinition) {
    questions.value[key] = q
  }

  function removeQuestion(key: string) {
    delete questions.value[key]
  }

  async function runDecision(apiKey?: string) {
    if (!inputText.value.trim()) {
      error.value = '请输入需要进行决策判断的文本内容'
      return
    }
    if (Object.keys(questions.value).length === 0) {
      error.value = '请至少配置一个决策问题 (Choice, Noul, 或 Score)'
      return
    }

    executing.value = true
    error.value = null

    try {
      const payload: DecisionRequest = {
        input: inputText.value,
        questions: questions.value,
        model: selectedModelId.value,
      }
      currentResponse.value = await predictDecision(payload, apiKey)
    } catch (err: any) {
      console.error('Decision execution error:', err)
      const msg = err.response?.data?.detail || err.message || '决策模型请求失败'
      error.value = msg
    } finally {
      executing.value = false
    }
  }

  return {
    templates,
    selectedTemplateId,
    selectedModelId,
    modelOptions,
    currentModelMeta,
    currentModelShortName,
    selectModel,
    inputText,
    questions,
    currentResponse,
    executing,
    error,
    loadTemplates,
    applyTemplate,
    addQuestion,
    updateQuestion,
    removeQuestion,
    runDecision,
  }
})
