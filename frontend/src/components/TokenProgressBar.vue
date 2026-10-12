<template>
  <div class="w-full">
    <div class="flex justify-between items-center text-xs mb-1">
      <span class="text-base-content/70">{{ label || 'Token 消耗' }}</span>
      <span class="font-medium">
        {{ formatNumber(used) }} / {{ limit > 0 ? formatNumber(limit) : '无上限' }}
        <span class="text-base-content/50 ml-1">({{ percent.toFixed(1) }}%)</span>
      </span>
    </div>
    <div class="w-full bg-base-300 rounded-full h-2 overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-500"
        :class="barColor"
        :style="{ width: `${Math.min(100, Math.max(0, percent))}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    used: number
    limit: number
    label?: string
  }>(),
  {
    limit: 500000,
  }
)

const percent = computed(() => {
  if (props.limit <= 0) return 0
  return Math.min(100, (props.used / props.limit) * 100)
})

const barColor = computed(() => {
  if (percent.value >= 90) return 'bg-error'
  if (percent.value >= 70) return 'bg-warning'
  return 'bg-primary'
})

function formatNumber(num: number) {
  return num.toLocaleString()
}
</script>
