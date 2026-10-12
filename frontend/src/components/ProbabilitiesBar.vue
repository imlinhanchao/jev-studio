<template>
  <div class="space-y-3">
    <!-- Choice Type (Categorical Probabilities) -->
    <div v-if="type === 'choice' && choiceData" class="space-y-2.5">
      <div class="flex items-center justify-between">
        <div class="text-xs sm:text-sm font-semibold flex items-center gap-1.5 flex-wrap">
          <span>预测分类:</span>
          <span class="badge badge-primary font-medium text-xs flex items-center gap-1">
            <span v-if="getOptionLetter(choiceData.choice)" class="font-bold">
              选项 {{ getOptionLetter(choiceData.choice) }}:
            </span>
            <span>{{ getOptionLabel(choiceData.choice) }}</span>
          </span>
        </div>
        <span class="text-xs text-base-content/60 font-mono">
          置信度: {{ (choiceData.confidence * 100).toFixed(1) }}%
        </span>
      </div>

      <div class="space-y-1.5 pt-0.5">
        <div
          v-for="(prob, optKey) in choiceData.probabilities"
          :key="optKey"
          class="space-y-1 bg-base-200/50 p-2 rounded-lg border border-base-300/50"
        >
          <div class="flex justify-between text-xs items-center gap-2">
            <div class="flex items-center gap-1.5 min-w-0">
              <span
                v-if="getOptionLetter(String(optKey))"
                class="badge badge-xs font-mono font-bold shrink-0"
                :class="optKey === choiceData.choice ? 'badge-primary' : 'badge-neutral'"
              >
                {{ getOptionLetter(String(optKey)) }}
              </span>
              <span class="truncate" :class="optKey === choiceData.choice ? 'font-bold text-primary' : 'text-base-content/80'">
                {{ getOptionLabel(String(optKey)) }}
              </span>
            </div>
            <span class="font-mono font-medium text-xs shrink-0" :class="optKey === choiceData.choice ? 'text-primary font-bold' : 'text-base-content/60'">
              {{ (prob * 100).toFixed(1) }}%
            </span>
          </div>
          <div class="w-full bg-base-300 rounded-full h-1.5 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="optKey === choiceData.choice ? 'bg-primary' : 'bg-base-content/25'"
              :style="{ width: `${prob * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Noul Type (Binary Yes/No Probability) -->
    <div v-else-if="type === 'noul' && noulData" class="space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold">
          判定结果:
          <span
            class="badge font-mono ml-1"
            :class="noulData.decision ? 'badge-success' : 'badge-neutral'"
          >
            {{ noulData.decision ? 'YES (符合)' : 'NO (不符合)' }}
          </span>
        </span>
        <span class="text-xs text-base-content/60 font-mono">
          概率: {{ (noulData.probability * 100).toFixed(1) }}%
        </span>
      </div>

      <div class="w-full bg-base-300 rounded-full h-2.5 overflow-hidden mt-2">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="noulData.decision ? 'bg-success' : 'bg-neutral'"
          :style="{ width: `${noulData.probability * 100}%` }"
        ></div>
      </div>
      <div class="flex justify-between text-xs text-base-content/50 font-mono text-[11px]">
        <span>0% (No)</span>
        <span>50% (判定阈值)</span>
        <span>100% (Yes)</span>
      </div>
    </div>

    <!-- Score Type (Ordinal Rubric) -->
    <div v-else-if="type === 'score' && scoreData" class="space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold">
          分值评分:
          <span class="badge badge-accent font-mono ml-1 text-sm font-bold">
            {{ scoreData.score }} / {{ scoreData.scale }} 分
          </span>
        </span>
        <span class="text-xs text-base-content/60 font-mono">
          置信度: {{ (scoreData.confidence * 100).toFixed(1) }}%
        </span>
      </div>

      <div class="flex gap-1.5 pt-1">
        <div
          v-for="s in scoreData.scale"
          :key="s"
          class="flex-1 h-3 rounded transition-all flex items-center justify-center text-[9px] font-mono select-none"
          :class="s <= scoreData.score ? 'bg-accent text-accent-content font-bold shadow-sm' : 'bg-base-300 text-base-content/40'"
        >
          {{ s }}
        </div>
      </div>
    </div>

    <!-- Generic Fallback -->
    <div v-else class="text-xs font-mono bg-base-300 p-2 rounded">
      {{ JSON.stringify(data) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { QuestionType } from '@/types/decision'

const props = defineProps<{
  type: QuestionType
  data: any
  criteria?: Record<string, string> | string
}>()

const choiceData = computed(() => (props.type === 'choice' ? props.data : null))
const noulData = computed(() => (props.type === 'noul' ? props.data : null))
const scoreData = computed(() => (props.type === 'score' ? props.data : null))

function isRecord(val: any): val is Record<string, string> {
  return typeof val === 'object' && val !== null && !Array.isArray(val)
}

function getOptionLabel(key: string): string {
  if (props.criteria && isRecord(props.criteria) && props.criteria[key]) {
    return props.criteria[key]
  }
  return key
}

function getOptionLetter(key: string): string {
  if (props.criteria && isRecord(props.criteria)) {
    const keys = Object.keys(props.criteria)
    const idx = keys.indexOf(key)
    if (idx >= 0) {
      return String.fromCharCode(65 + idx)
    }
  }
  return ''
}
</script>
