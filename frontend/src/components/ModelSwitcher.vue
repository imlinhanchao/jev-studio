<template>
  <!-- Shared trigger (identical in Console & Playground headers) -->
  <button
    class="btn btn-sm btn-ghost border border-base-300 bg-base-200/60 hover:bg-base-200 gap-1.5 font-normal px-2.5 max-w-[16rem]"
    :title="isBusy ? modelStore.progress.message || statusText : '点击切换 / 管理决策模型'"
    @click="open = true"
  >
    <template v-if="isBusy">
      <span class="loading loading-spinner loading-xs text-primary"></span>
      <span class="text-xs font-bold whitespace-nowrap">{{ progressLabel }}</span>
      <progress class="progress progress-primary w-14 h-1.5" :value="modelStore.progress.percent" max="100"></progress>
    </template>
    <template v-else>
      <span class="relative flex h-2 w-2 flex-shrink-0">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="modelDotClass"></span>
        <span class="relative inline-flex rounded-full h-2 w-2" :class="modelDotClass"></span>
      </span>
      <span class="text-xs font-bold truncate">{{ shortName }}</span>
      <span class="badge badge-xs font-mono hidden sm:inline-flex" :class="tagBadgeClass">{{ shortTag }}</span>
      <span class="text-[10px] font-medium hidden md:inline" :class="statusTextClass">{{ statusLabel }}</span>
    </template>
    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 opacity-60 ml-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
    </svg>
  </button>

  <!-- Model management modal -->
  <Teleport to="body">
    <dialog class="modal" :class="{ 'modal-open': open }">
      <div class="modal-box max-w-xl">
        <h3 class="font-bold text-lg flex items-center justify-between pb-2 border-b border-base-300">
          <div class="flex items-center gap-2">
            <span>🧠 决策模型管理与运行状态</span>
          </div>
          <button class="btn btn-xs btn-ghost btn-circle" @click="open = false">✕</button>
        </h3>

        <div class="py-4 space-y-4">
          <!-- Loading Progress -->
          <div v-if="modelStore.isBusy" class="bg-base-200/60 rounded-xl p-3.5 border border-base-300 space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="font-semibold text-base-content/80 flex items-center gap-2">
                <span class="loading loading-spinner loading-xs"></span>
                模型载入中
              </span>
              <span class="font-mono text-primary">{{ Math.round(modelStore.progress.percent) }}%</span>
            </div>
            <progress class="progress progress-primary w-full" :value="modelStore.progress.percent" max="100"></progress>
            <div class="text-[11px] text-base-content/60 font-mono truncate" :title="modelStore.progress.message">
              {{ modelStore.progress.message || modelStore.progress.state }}
            </div>
          </div>

          <!-- Simple cache toggle -->
          <div class="flex items-center justify-between bg-base-200/60 rounded-xl px-3.5 py-3 border border-base-300">
            <div class="pr-3">
              <div class="text-xs font-semibold text-base-content/80">简单缓存（保留已加载模型）</div>
              <div class="text-[10px] text-base-content/55 leading-snug">
                开启后，切回已载入过的模型无需重新载入；关闭则每次切换仅保留当前模型。
              </div>
            </div>
            <input
              type="checkbox"
              class="toggle toggle-primary toggle-sm"
              :checked="modelStore.cacheEnabled"
              :disabled="modelStore.actionLoading"
              @change="onToggleCache"
            />
          </div>

          <!-- Model List & Switcher -->
          <div>
            <div class="text-xs font-semibold text-base-content/70 mb-2.5">
              可选决策模型 (点击切换当前活跃模型):
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div
                v-for="m in modelStore.availableModels"
                :key="m.id"
                class="p-3.5 rounded-xl border transition-all cursor-pointer relative"
                :class="m.id === modelStore.activeModelId ? 'border-primary bg-primary/10 shadow-sm' : 'border-base-300 bg-base-200 hover:border-base-content/30'"
                @click="onSwitch(m.id)"
              >
                <div class="flex items-center justify-between mb-1.5">
                  <span class="font-bold text-xs flex items-center gap-1.5">
                    {{ m.name }}
                    <span v-if="m.is_loaded" class="badge badge-success badge-xs font-normal">已加载</span>
                  </span>
                  <span
                    class="badge badge-xs font-mono"
                    :class="m.id === modelStore.activeModelId ? 'badge-primary' : 'badge-ghost'"
                  >
                    {{ m.id === modelStore.activeModelId ? '当前生效' : '点击切换' }}
                  </span>
                </div>
                <div class="text-[11px] text-base-content/70 line-clamp-2 mb-2 leading-relaxed">
                  {{ m.description }}
                </div>
                <div class="flex items-center justify-between text-[10px] text-base-content/60 font-mono">
                  <span>{{ m.parameters }} · {{ m.provider }}</span>
                  <span class="text-success">{{ m.typical_latency_ms }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Current Active Model Details -->
          <div class="bg-base-200/60 rounded-xl p-3.5 border border-base-300 space-y-2 text-xs" v-if="modelStore.status">
            <div class="font-semibold text-base-content/80 text-xs mb-1">
              当前活跃模型运行参数:
            </div>
            <div class="flex justify-between border-b border-base-300/50 pb-1.5">
              <span class="text-base-content/60">当前模型标识:</span>
              <span class="font-mono font-medium text-primary">{{ modelStore.status.model_id }}</span>
            </div>
            <div class="flex justify-between border-b border-base-300/50 pb-1.5">
              <span class="text-base-content/60">模型架构:</span>
              <span class="font-mono text-xs">{{ modelStore.status.architecture }}</span>
            </div>
            <div class="flex justify-between border-b border-base-300/50 pb-1.5">
              <span class="text-base-content/60">运行引擎状态:</span>
              <span class="badge badge-xs font-medium" :class="engineBadgeClass">{{ engineStateText }}</span>
            </div>
            <div class="flex justify-between border-b border-base-300/50 pb-1.5">
              <span class="text-base-content/60">加速计算设备:</span>
              <span class="badge badge-outline badge-xs uppercase">{{ modelStore.status.device }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-base-content/60">支持决策原语:</span>
              <span class="text-xs">Choice, Noul, Score</span>
            </div>
            <div v-if="modelStore.status.load_error" class="alert alert-warning text-xs mt-2 py-2">
              <span>权重状态: {{ modelStore.status.load_error }}</span>
            </div>
          </div>

          <!-- Resident / cached models -->
          <div class="bg-base-200/60 rounded-xl p-3.5 border border-base-300 space-y-2" v-if="modelStore.status">
            <div class="flex items-center justify-between mb-1">
              <span class="font-semibold text-base-content/80 text-xs">
                内存中已载入模型 ({{ modelStore.loadedModels.length }})
              </span>
              <span class="badge badge-xs" :class="modelStore.cacheEnabled ? 'badge-primary' : 'badge-ghost'">
                {{ modelStore.cacheEnabled ? '简单缓存开启' : '单模型模式' }}
              </span>
            </div>
            <div v-if="modelStore.loadedModels.length === 0" class="text-[11px] text-base-content/50">
              当前没有模型驻留内存。
            </div>
            <div
              v-for="mid in modelStore.loadedModels"
              :key="mid"
              class="flex items-center justify-between gap-2 text-xs border-b border-base-300/50 pb-1.5 last:border-0 last:pb-0"
            >
              <span class="font-mono truncate" :title="mid">{{ modelName(mid) }}</span>
              <div class="flex items-center gap-2 flex-shrink-0">
                <span v-if="mid === modelStore.activeModelId" class="badge badge-primary badge-xs">活跃</span>
                <button
                  class="btn btn-xs btn-ghost text-error"
                  :disabled="modelStore.actionLoading"
                  @click="modelStore.triggerUnload(mid)"
                >
                  卸载
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-action flex justify-between items-center pt-2 border-t border-base-300">
          <button
            class="btn btn-sm btn-outline btn-primary"
            :disabled="modelStore.actionLoading"
            @click="modelStore.triggerLoadReal(true)"
          >
            <span v-if="modelStore.actionLoading" class="loading loading-spinner loading-xs"></span>
            加载 / 重载权重
          </button>
          <button class="btn btn-sm" @click="open = false">关闭</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="open = false">
        <button>close</button>
      </form>
    </dialog>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useModelStore } from '@/stores/modelStore'
import { useDecisionStore } from '@/stores/decisionStore'

const modelStore = useModelStore()
const decisionStore = useDecisionStore()
const open = ref(false)

const isBusy = computed(() => modelStore.isBusy)

onMounted(() => {
  modelStore.loadStatus()
})

function modelName(id: string) {
  return modelStore.availableModels.find((m) => m.id === id)?.name || id
}

function onToggleCache(e: Event) {
  const target = e.target as HTMLInputElement
  modelStore.updateCacheMode(target.checked)
}

async function onSwitch(id: string) {
  decisionStore.selectModel(id)
  await modelStore.switchModel(id)
}

const shortName = computed(() => {
  const id = modelStore.activeModelId || ''
  if (id.includes('EdgeJev')) return 'EdgeJev'
  if (id.includes('MiniCPM')) return 'MiniCPM5-2B'
  return 'd1-omni-600M'
})

const shortTag = computed(() => {
  const id = modelStore.activeModelId || ''
  if (id.includes('EdgeJev')) return '322M Edge'
  if (id.includes('MiniCPM')) return '2.0B Jev'
  return '600M LFM'
})

const statusLabel = computed(() => {
  if (modelStore.loading) return '检测中'
  if (modelStore.status?.mode === 'real') return '已加载'
  if (modelStore.status?.mode === 'error') return '载入失败'
  return '未载入'
})

const progressLabel = computed(() => {
  const state = modelStore.progress.state
  const map: Record<string, string> = {
    preparing: '准备中',
    downloading: '下载中',
    loading: '载入中',
    ready: '已完成',
    error: '载入失败',
  }
  const prefix = map[state] || '载入中'
  return `${prefix} ${Math.round(modelStore.progress.percent)}%`
})

const statusText = computed(() => `${shortName.value} (${statusLabel.value})`)

const engineStateText = computed(() => {
  if (modelStore.status?.is_loading) return '正在载入权重...'
  if (modelStore.status?.mode === 'real') return '本地 PyTorch 原生推理'
  if (modelStore.status?.mode === 'error') return '权重载入失败'
  return '模型未载入'
})

const engineBadgeClass = computed(() => {
  if (modelStore.status?.mode === 'real') return 'badge-success'
  if (modelStore.status?.mode === 'error') return 'badge-error'
  return 'badge-warning'
})

const tagBadgeClass = computed(() => {
  if (modelStore.status?.mode === 'real') return 'badge-success'
  if (modelStore.status?.mode === 'error') return 'badge-error'
  return 'badge-neutral'
})

const statusTextClass = computed(() => {
  if (modelStore.status?.mode === 'real') return 'text-success'
  if (modelStore.status?.mode === 'error') return 'text-error'
  return 'text-base-content/50'
})

const modelDotClass = computed(() => {
  if (modelStore.status?.mode === 'real') return 'bg-success'
  if (modelStore.status?.mode === 'error') return 'bg-error'
  return 'bg-primary'
})
</script>
