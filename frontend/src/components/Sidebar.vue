<template>
  <aside class="w-64 bg-base-200 border-r border-base-300 flex flex-col h-full min-h-screen text-base-content">
    <!-- Brand / Logo -->
    <div class="p-5 border-b border-base-300 flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-content font-black text-xl shadow-md">
        J
      </div>
      <div>
        <div class="font-bold text-base tracking-wide flex items-center gap-1.5">
          <span>JEV 决策中台</span>
        </div>
        <div class="text-[11px] text-base-content/60 font-mono">
          Liquid AI d1-omni
        </div>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="flex-1 p-3 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors hover:bg-base-300"
        :class="{ 'bg-primary text-primary-content hover:bg-primary/90 font-semibold shadow-sm': isActive(item.path) }"
      >
        <component :is="item.icon" class="w-4 h-4 flex-shrink-0" />
        <span>{{ item.label }}</span>
        <span v-if="item.badge" class="badge badge-xs ml-auto" :class="isActive(item.path) ? 'badge-ghost' : 'badge-neutral'">
          {{ item.badge }}
        </span>
      </router-link>
    </nav>

    <!-- Bottom Status Box -->
    <div class="p-3 border-t border-base-300 space-y-2">
      <div class="bg-base-300/50 rounded-lg p-2.5 text-xs space-y-1.5 border border-base-300">
        <div class="flex items-center justify-between font-semibold text-base-content/80">
          <span>调试 API Key</span>
          <span class="badge badge-xs badge-success">生效中</span>
        </div>
        <div class="font-mono text-[11px] truncate text-base-content/60">
          {{ keyStore.activePlaygroundKey ? keyStore.activePlaygroundKey.slice(0, 14) + '...' : '未配置 (使用默认)' }}
        </div>
      </div>

      <!-- Current Admin User & Quick Logout -->
      <div class="flex items-center justify-between px-1 text-xs">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-xs uppercase flex-shrink-0">
            {{ (authStore.user?.username || 'A')[0] }}
          </div>
          <div class="truncate">
            <span class="font-medium text-base-content/80">{{ authStore.user?.username || 'admin' }}</span>
          </div>
        </div>
        <button
          class="btn btn-ghost btn-xs text-error p-1 hover:bg-error/10"
          title="退出登录"
          @click="handleLogout"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { h } from 'vue'
import { useKeyStore } from '@/stores/keyStore'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const router = useRouter()
const keyStore = useKeyStore()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

// Inline SVG icons for seamless bundle stability
const HomeIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })
])

const StudioIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z' }),
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
])

const KeyIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z' })
])

const ChartIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })
])

const DocIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
])

const navItems = [
  { path: '/', label: '控制台概览', icon: HomeIcon },
  { path: '/playground', label: '决策 Studio', icon: StudioIcon, badge: 'Live' },
  { path: '/api-keys', label: 'API Key 管理', icon: KeyIcon },
  { path: '/analytics', label: 'Token 消耗统计', icon: ChartIcon },
  { path: '/docs', label: '开发者文档', icon: DocIcon },
]
</script>
