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
      <!-- Model Status Badge & Switcher -->
      <ModelSwitcher />

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
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import ModelSwitcher from '@/components/ModelSwitcher.vue'

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>
