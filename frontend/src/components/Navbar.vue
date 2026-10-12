<template>
  <header class="navbar bg-base-100/80 backdrop-blur border-b border-base-300 sticky top-0 z-30 px-4 gap-2">
    <!-- Mobile hamburger button -->
    <div class="flex-none lg:hidden">
      <label for="app-drawer" class="btn btn-square btn-ghost">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
      </label>
    </div>

    <!-- Title and Page Context -->
    <div class="flex-1 flex items-center gap-2">
      <span class="font-bold text-lg hidden sm:inline-block bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
        JEV 决策模型 API
      </span>
      <div class="badge badge-outline badge-sm hidden md:inline-flex font-mono">
        v1.0.0
      </div>
    </div>

    <!-- Right Controls -->
    <div class="flex-none flex items-center gap-2 sm:gap-3">
      <!-- Model Status Badge -->
      <div
        class="badge gap-1.5 py-3 px-3 cursor-pointer select-none transition-all hover:opacity-80"
        :class="modelBadgeClass"
        @click="showModelModal = true"
        title="点击查看 Liquid AI 模型状态"
      >
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="modelDotClass"></span>
          <span class="relative inline-flex rounded-full h-2 w-2" :class="modelDotClass"></span>
        </span>
        <span class="font-medium text-xs">
          {{ modelStatusText }}
        </span>
      </div>

      <!-- Theme Controller Dropdown -->
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-sm btn-ghost gap-1 font-normal">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
          <span class="capitalize text-xs hidden sm:inline">{{ themeStore.currentTheme }}</span>
        </div>
        <ul tabindex="0" class="dropdown-content menu p-2 shadow-lg bg-base-200 rounded-box w-36 z-50 text-xs">
          <li v-for="t in ['dark', 'light', 'synthwave', 'corporate', 'dim']" :key="t">
            <button
              :class="{ 'active': themeStore.currentTheme === t }"
              @click="themeStore.setTheme(t)"
            >
              {{ t }}
            </button>
          </li>
        </ul>
      </div>

      <!-- Admin User Profile Dropdown -->
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-sm btn-ghost gap-2 font-normal pl-2 pr-3">
          <div class="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-xs uppercase">
            {{ (authStore.user?.username || 'A')[0] }}
          </div>
          <span class="text-xs font-medium hidden sm:inline">{{ authStore.user?.username || 'admin' }}</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 opacity-60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        <ul tabindex="0" class="dropdown-content menu p-2 shadow-xl bg-base-200 rounded-box w-48 z-50 text-xs border border-base-300">
          <li class="menu-title px-2 py-1 text-[11px] text-base-content/60">
            中台管理员 (已登录)
          </li>
          <li>
            <div class="flex items-center gap-2 py-2 font-mono text-[11px] text-base-content/80">
              <span class="badge badge-success badge-xs"></span>
              <span>账号: {{ authStore.user?.username || 'admin' }}</span>
            </div>
          </li>
          <div class="divider my-1"></div>
          <li>
            <button class="text-error hover:bg-error/10 flex items-center gap-2" @click="handleLogout">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>退出登录</span>
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Model Status & Selection Modal -->
    <dialog class="modal" :class="{ 'modal-open': showModelModal }">
      <div class="modal-box max-w-xl">
        <h3 class="font-bold text-lg flex items-center justify-between pb-2 border-b border-base-300">
          <div class="flex items-center gap-2">
            <span>🧠 决策模型管理与运行状态</span>
          </div>
          <button class="btn btn-xs btn-ghost btn-circle" @click="showModelModal = false">✕</button>
        </h3>
        
        <!-- Model List & Switcher -->
        <div class="py-4 space-y-4">
          <div>
            <div class="text-xs font-semibold text-base-content/70 mb-2.5">
              可选决策模型 (点击切换当前中台活跃模型):
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div
                v-for="m in modelStore.availableModels"
                :key="m.id"
                class="p-3.5 rounded-xl border transition-all cursor-pointer relative"
                :class="m.id === modelStore.activeModelId ? 'border-primary bg-primary/10 shadow-sm' : 'border-base-300 bg-base-200 hover:border-base-content/30'"
                @click="modelStore.switchModel(m.id)"
              >
                <div class="flex items-center justify-between mb-1.5">
                  <span class="font-bold text-xs">{{ m.name }}</span>
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
              <span class="badge badge-xs font-medium" :class="modelStore.status.mode === 'real' ? 'badge-success' : 'badge-info'">
                {{ modelStore.status.mode === 'real' ? '本地 PyTorch 原生推理' : '高精度校准仿真引擎' }}
              </span>
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
          <button class="btn btn-sm" @click="showModelModal = false">关闭</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="showModelModal = false">
        <button>close</button>
      </form>
    </dialog>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/themeStore'
import { useModelStore } from '@/stores/modelStore'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const themeStore = useThemeStore()
const modelStore = useModelStore()
const authStore = useAuthStore()
const showModelModal = ref(false)

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  modelStore.loadStatus()
})

const modelStatusText = computed(() => {
  if (modelStore.loading) return '检测模型中...'
  const isEdgeJev = modelStore.activeModelId?.includes('EdgeJev')
  const isMiniCPM = modelStore.activeModelId?.includes('MiniCPM')
  const shortName = isEdgeJev ? 'EdgeJev' : (isMiniCPM ? 'MiniCPM5-2B' : 'd1-omni-600M')
  if (modelStore.status?.mode === 'real') return `${shortName} (已加载)`
  return `${shortName} (在线)`
})

const modelBadgeClass = computed(() => {
  if (modelStore.status?.mode === 'real') return 'badge-success text-success-content'
  return 'badge-primary text-primary-content'
})

const modelDotClass = computed(() => {
  if (modelStore.status?.mode === 'real') return 'bg-success-content'
  return 'bg-primary-content'
})
</script>
