<template>
  <div class="space-y-6">
    <!-- Header Banner -->
    <div class="card bg-gradient-to-r from-primary/10 via-base-200 to-accent/10 border border-base-300 shadow-sm">
      <div class="card-body p-6 md:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-black tracking-tight">JEV 决策中台控制台</h1>
            <span class="badge badge-primary badge-sm">d1-omni-600M</span>
          </div>
          <p class="text-sm text-base-content/70 max-w-xl">
            基于 Liquid AI 零生成单步前向决策架构，支持分类 (Choice)、判断 (Noul) 与打分 (Score) 等多任务并行处理。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <router-link to="/playground" class="btn btn-primary btn-sm md:btn-md gap-2 shadow-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            启动决策 Studio
          </router-link>
          <router-link to="/api-keys" class="btn btn-outline btn-sm md:btn-md">
            开通 API Key
          </router-link>
        </div>
      </div>
    </div>

    <!-- KPI Metric Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" v-if="analyticsStore.dashboard">
      <StatCard
        title="总调用次数"
        :value="analyticsStore.dashboard.summary.total_requests.toLocaleString()"
        subtext="实时代币化请求"
        iconBgClass="bg-blue-500/10 text-blue-500"
      >
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </template>
      </StatCard>

      <StatCard
        title="Token 消耗总量"
        :value="analyticsStore.dashboard.summary.total_tokens.toLocaleString()"
        :subtext="`Prompt: ${analyticsStore.dashboard.summary.prompt_tokens.toLocaleString()} | Decision: ${analyticsStore.dashboard.summary.decision_tokens.toLocaleString()}`"
        iconBgClass="bg-emerald-500/10 text-emerald-500"
      >
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </template>
      </StatCard>

      <StatCard
        title="平均推理延迟"
        :value="`${analyticsStore.dashboard.summary.avg_latency_ms} ms`"
        subtext="Liquid AI 毫秒级极速响应"
        iconBgClass="bg-purple-500/10 text-purple-500"
      >
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </template>
      </StatCard>

      <StatCard
        title="活跃 API Key"
        :value="`${analyticsStore.dashboard.summary.active_keys_count} / ${analyticsStore.dashboard.summary.total_keys_count}`"
        subtext="具备 Token 配额保障"
        iconBgClass="bg-amber-500/10 text-amber-500"
      >
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
        </template>
      </StatCard>
    </div>

    <!-- Loading skeleton -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="card bg-base-200 h-28 animate-pulse"></div>
    </div>

    <!-- Charts & Breakdown Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 7-Day Trend Chart -->
      <div class="card bg-base-200 border border-base-300 lg:col-span-2">
        <div class="card-body p-5">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="card-title text-base font-bold">Token 消耗与调用趋势</h2>
              <p class="text-xs text-base-content/60">近 7 天每日调用次数与 Token 吞吐情况</p>
            </div>
            <span class="badge badge-sm badge-outline">Daily</span>
          </div>

          <!-- Trend Bar Graph -->
          <div v-if="analyticsStore.dashboard?.timeseries?.length" class="h-56 flex items-end gap-3 pt-6 px-2">
            <div
              v-for="point in analyticsStore.dashboard.timeseries"
              :key="point.date"
              class="flex-1 flex flex-col items-center gap-2 h-full justify-end group"
            >
              <!-- Tooltip info -->
              <div class="text-[10px] text-base-content/70 opacity-0 group-hover:opacity-100 transition-opacity font-mono">
                {{ point.tokens }} tokens
              </div>
              <!-- Bar -->
              <div
                class="w-full rounded-t-lg bg-primary group-hover:bg-primary/80 transition-all"
                :style="{ height: `${Math.max(12, Math.min(100, (point.tokens / maxTokens) * 100))}%` }"
              ></div>
              <!-- Label -->
              <span class="text-[10px] text-base-content/60 font-mono truncate max-w-full">
                {{ point.date.slice(5) }}
              </span>
            </div>
          </div>
          <div v-else class="h-48 flex items-center justify-center text-sm text-base-content/50">
            暂无趋势数据
          </div>
        </div>
      </div>

      <!-- Decision Type Distribution -->
      <div class="card bg-base-200 border border-base-300">
        <div class="card-body p-5">
          <h2 class="card-title text-base font-bold mb-1">决策原语任务分布</h2>
          <p class="text-xs text-base-content/60 mb-4">Choice / Noul / Score 调用占比</p>

          <div v-if="analyticsStore.dashboard" class="space-y-4 pt-2">
            <!-- Choice -->
            <div class="space-y-1">
              <div class="flex justify-between text-xs">
                <span class="font-medium flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-primary inline-block"></span>
                  Choice (分类选择)
                </span>
                <span class="font-mono font-semibold">{{ analyticsStore.dashboard.type_distribution.choice }}</span>
              </div>
              <div class="w-full bg-base-300 rounded-full h-2">
                <div
                  class="bg-primary h-2 rounded-full"
                  :style="{ width: `${distributionPercent.choice}%` }"
                ></div>
              </div>
            </div>

            <!-- Noul -->
            <div class="space-y-1">
              <div class="flex justify-between text-xs">
                <span class="font-medium flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>
                  Noul (二元判断 Yes/No)
                </span>
                <span class="font-mono font-semibold">{{ analyticsStore.dashboard.type_distribution.noul }}</span>
              </div>
              <div class="w-full bg-base-300 rounded-full h-2">
                <div
                  class="bg-emerald-500 h-2 rounded-full"
                  :style="{ width: `${distributionPercent.noul}%` }"
                ></div>
              </div>
            </div>

            <!-- Score -->
            <div class="space-y-1">
              <div class="flex justify-between text-xs">
                <span class="font-medium flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-accent inline-block"></span>
                  Score (量规打分)
                </span>
                <span class="font-mono font-semibold">{{ analyticsStore.dashboard.type_distribution.score }}</span>
              </div>
              <div class="w-full bg-base-300 rounded-full h-2">
                <div
                  class="bg-accent h-2 rounded-full"
                  :style="{ width: `${distributionPercent.score}%` }"
                ></div>
              </div>
            </div>

            <!-- Tip -->
            <div class="bg-base-300/40 p-3 rounded-lg text-xs text-base-content/70 mt-4 leading-relaxed">
              💡 Liquid AI 支持单次推理中同时评估多种决策原语，共享底层输入上下文表示，零生成开销。
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active API Keys Table Preview -->
    <div class="card bg-base-200 border border-base-300">
      <div class="card-body p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="card-title text-base font-bold">API Key 消耗排行</h2>
            <p class="text-xs text-base-content/60">当前已开通凭证及其代币配额使用进度</p>
          </div>
          <router-link to="/api-keys" class="btn btn-sm btn-ghost text-primary text-xs">
            管理全部 Key →
          </router-link>
        </div>

        <div class="overflow-x-auto">
          <table class="table table-sm">
            <thead>
              <tr class="text-base-content/60">
                <th>名称</th>
                <th>前缀凭证</th>
                <th>Token 消耗配额</th>
                <th>调用次数</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in analyticsStore.dashboard?.key_usage || []" :key="item.key_id" class="hover">
                <td class="font-medium">{{ item.name }}</td>
                <td class="font-mono text-xs">{{ item.key_prefix }}</td>
                <td class="w-72">
                  <TokenProgressBar :used="item.tokens_used" :limit="item.token_limit" />
                </td>
                <td class="font-mono text-xs">{{ item.requests_count }} 次</td>
                <td>
                  <span
                    class="badge badge-xs"
                    :class="item.is_active ? 'badge-success' : 'badge-ghost'"
                  >
                    {{ item.is_active ? '启用' : '禁用' }}
                  </span>
                </td>
              </tr>
              <tr v-if="!analyticsStore.dashboard?.key_usage?.length">
                <td colspan="5" class="text-center text-sm text-base-content/50 py-6">
                  暂无 API Key 记录
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
import { computed, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import StatCard from '@/components/StatCard.vue'
import TokenProgressBar from '@/components/TokenProgressBar.vue'

const analyticsStore = useAnalyticsStore()

onMounted(async () => {
  await analyticsStore.loadDashboard()
})

const maxTokens = computed(() => {
  if (!analyticsStore.dashboard?.timeseries?.length) return 100
  const max = Math.max(...analyticsStore.dashboard.timeseries.map(t => t.tokens))
  return max > 0 ? max : 100
})

const distributionPercent = computed(() => {
  if (!analyticsStore.dashboard) return { choice: 0, noul: 0, score: 0 }
  const total =
    analyticsStore.dashboard.type_distribution.choice +
    analyticsStore.dashboard.type_distribution.noul +
    analyticsStore.dashboard.type_distribution.score
  if (total === 0) return { choice: 0, noul: 0, score: 0 }
  return {
    choice: Math.round((analyticsStore.dashboard.type_distribution.choice / total) * 100),
    noul: Math.round((analyticsStore.dashboard.type_distribution.noul / total) * 100),
    score: Math.round((analyticsStore.dashboard.type_distribution.score / total) * 100),
  }
})
</script>
