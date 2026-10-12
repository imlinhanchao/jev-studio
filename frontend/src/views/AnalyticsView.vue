<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight flex items-center gap-2">
          <span>Token 消耗统计与审计</span>
          <span class="badge badge-accent badge-sm">Usage Analytics</span>
        </h1>
        <p class="text-xs text-base-content/60 mt-1">
          全链路追踪 Liquid AI d1-omni-600M 每次推理调用的 Prompt 算力与 Decision 算力消耗
        </p>
      </div>

      <div class="flex items-center gap-2">
        <select
          v-model="selectedKeyFilter"
          class="select select-bordered select-xs text-xs font-mono"
          @change="reloadLogs"
        >
          <option :value="undefined">全部 API Key</option>
          <option v-for="k in keyStore.keys" :key="k.id" :value="k.id">
            {{ k.name }} ({{ k.key_prefix }})
          </option>
        </select>
        <button
          class="btn btn-sm btn-outline gap-1"
          :disabled="analyticsStore.loading"
          @click="refreshAll"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" :class="{ 'animate-spin': analyticsStore.loading }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          刷新
        </button>
      </div>
    </div>

    <!-- Quick Token Summary Breakdown -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4" v-if="analyticsStore.dashboard">
      <div class="card bg-base-200 border border-base-300 p-4">
        <div class="text-xs text-base-content/60 font-semibold uppercase">总消耗 Token</div>
        <div class="text-2xl font-black text-primary mt-1">
          {{ analyticsStore.dashboard.summary.total_tokens.toLocaleString() }}
        </div>
        <div class="text-[11px] text-base-content/50 mt-1">Prompt 与 Decision 计算单元总和</div>
      </div>

      <div class="card bg-base-200 border border-base-300 p-4">
        <div class="text-xs text-base-content/60 font-semibold uppercase">Prompt 输入 Token</div>
        <div class="text-2xl font-black text-secondary mt-1">
          {{ analyticsStore.dashboard.summary.prompt_tokens.toLocaleString() }}
        </div>
        <div class="text-[11px] text-base-content/50 mt-1">包含输入文本与问题 Prompt 指令</div>
      </div>

      <div class="card bg-base-200 border border-base-300 p-4">
        <div class="text-xs text-base-content/60 font-semibold uppercase">Decision 决策算力 Token</div>
        <div class="text-2xl font-black text-accent mt-1">
          {{ analyticsStore.dashboard.summary.decision_tokens.toLocaleString() }}
        </div>
        <div class="text-[11px] text-base-content/50 mt-1">多任务分类与打分单步前向传播消耗</div>
      </div>
    </div>

    <!-- Usage Logs Audit Table -->
    <div class="card bg-base-200 border border-base-300">
      <div class="card-body p-0">
        <div class="p-4 border-b border-base-300 flex justify-between items-center">
          <div>
            <h2 class="card-title text-base font-bold">详细调用审计日志 (Audit Logs)</h2>
            <p class="text-xs text-base-content/60">每次决策请求的请求流水号、决策类型、延迟与代币消耗明细</p>
          </div>
          <span class="badge badge-sm badge-outline font-mono">
            {{ analyticsStore.logs.length }} 条记录
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="table table-sm">
            <thead>
              <tr class="bg-base-300/40 text-base-content/70 text-xs">
                <th>请求流水号</th>
                <th>关联 API Key</th>
                <th>评估决策类型</th>
                <th class="text-right">Prompt</th>
                <th class="text-right">Decision</th>
                <th class="text-right font-bold text-primary">总消耗</th>
                <th class="text-right">延迟</th>
                <th>状态</th>
                <th>调用时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in analyticsStore.logs" :key="log.id" class="hover border-b border-base-300/40 font-mono text-xs">
                <!-- Request ID -->
                <td class="font-bold text-base-content/80">{{ log.request_id }}</td>

                <!-- Key info -->
                <td>
                  <div class="text-xs font-sans font-medium text-base-content">
                    {{ log.key_name || '默认凭证' }}
                  </div>
                  <div class="text-[10px] text-base-content/50">{{ log.key_prefix || '系统级' }}</div>
                </td>

                <!-- Decision Types -->
                <td>
                  <div class="flex gap-1 flex-wrap">
                    <span
                      v-for="t in log.decision_types.split(',')"
                      :key="t"
                      class="badge badge-xs uppercase font-mono"
                    >
                      {{ t }}
                    </span>
                  </div>
                </td>

                <!-- Token breakdown -->
                <td class="text-right text-base-content/70">{{ log.prompt_tokens }}</td>
                <td class="text-right text-base-content/70">{{ log.decision_tokens }}</td>
                <td class="text-right font-bold text-primary">{{ log.total_tokens }}</td>

                <!-- Latency -->
                <td class="text-right">{{ log.latency_ms }} ms</td>

                <!-- Status -->
                <td>
                  <span class="badge badge-xs" :class="log.status_code === 200 ? 'badge-success' : 'badge-error'">
                    {{ log.status_code }}
                  </span>
                </td>

                <!-- Timestamp -->
                <td class="text-[11px] font-sans text-base-content/60">
                  {{ formatDate(log.created_at) }}
                </td>
              </tr>

              <tr v-if="analyticsStore.logs.length === 0">
                <td colspan="9" class="text-center py-10 text-sm font-sans text-base-content/50">
                  暂无调用日志。可在“决策 Studio”中发起测试，或通过 API 调用。
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import { useKeyStore } from '@/stores/keyStore'

const analyticsStore = useAnalyticsStore()
const keyStore = useKeyStore()

const selectedKeyFilter = ref<number | undefined>(undefined)

onMounted(async () => {
  await Promise.all([
    keyStore.loadKeys(),
    analyticsStore.loadDashboard(),
    analyticsStore.loadLogs(),
  ])
})

async function refreshAll() {
  await Promise.all([
    analyticsStore.loadDashboard(),
    analyticsStore.loadLogs(0, 50, selectedKeyFilter.value),
  ])
}

async function reloadLogs() {
  await analyticsStore.loadLogs(0, 50, selectedKeyFilter.value)
}

function formatDate(iso: string) {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return iso
  }
}
</script>
