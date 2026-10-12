<template>
  <div class="relative bg-base-300 rounded-lg p-3 overflow-hidden text-xs font-mono">
    <div class="absolute top-2 right-2 z-10">
      <CopyButton :text="formattedJson" textLabel="复制 JSON" />
    </div>
    <pre class="overflow-x-auto max-h-96 text-base-content/90">{{ formattedJson }}</pre>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CopyButton from './CopyButton.vue'

const props = defineProps<{
  data: any
}>()

const formattedJson = computed(() => {
  try {
    return JSON.stringify(props.data, null, 2)
  } catch {
    return String(props.data)
  }
})
</script>
