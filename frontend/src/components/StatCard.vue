<template>
  <div class="card bg-base-200/60 border border-base-300 shadow-sm hover:shadow-md transition-shadow">
    <div class="card-body p-5">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold uppercase tracking-wider text-base-content/60">{{ title }}</span>
        <div class="p-2 rounded-lg" :class="iconBgClass">
          <slot name="icon">
            <span class="text-lg">📊</span>
          </slot>
        </div>
      </div>
      <div class="mt-2">
        <div class="text-2xl font-bold tracking-tight text-base-content">{{ value }}</div>
        <div v-if="subtext" class="text-xs text-base-content/60 mt-1 flex items-center gap-1">
          <span>{{ subtext }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    value: string | number
    subtext?: string
    iconBgClass?: string
  }>(),
  {
    iconBgClass: 'bg-primary/10 text-primary',
  }
)
</script>
