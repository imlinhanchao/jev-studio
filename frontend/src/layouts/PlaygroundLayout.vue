<template>
  <div class="min-h-screen bg-base-100 text-base-content flex flex-col">
    <!-- Dedicated Playground Header -->
    <header class="navbar bg-base-100/90 backdrop-blur border-b border-base-300 sticky top-0 z-30 px-3 sm:px-6 gap-2 sm:gap-4 h-16">
      <!-- Left: Return to Console & Brand -->
      <div class="flex-1 flex items-center gap-2 sm:gap-3">
        <!-- Return Button -->
        <router-link
          to="/"
          class="btn btn-sm btn-ghost gap-1.5 text-base-content/75 hover:text-base-content px-2 sm:px-3"
          title="返回控制台概览"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span class="text-xs font-semibold hidden sm:inline">控制台</span>
        </router-link>

        <div class="divider divider-horizontal my-3 mx-0"></div>

        <!-- Logo / Studio Badge -->
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-content font-black text-sm shadow-sm">
            J
          </div>
          <div>
            <div class="font-black text-sm sm:text-base tracking-tight flex items-center gap-1.5 leading-none">
              <span>决策 Studio</span>
              <span class="badge badge-accent badge-xs font-mono font-bold">system_one</span>
            </div>
            <div class="text-[10px] text-base-content/50 font-mono hidden md:block mt-0.5">
              JEV Interactive Decision Studio
            </div>
          </div>
        </div>

        <!-- Quick Section Links -->
        <div class="hidden lg:flex items-center gap-1 ml-4 text-xs text-base-content/65">
          <router-link to="/api-keys" class="btn btn-xs btn-ghost font-normal hover:text-base-content">API Keys</router-link>
          <router-link to="/analytics" class="btn btn-xs btn-ghost font-normal hover:text-base-content">Token 统计</router-link>
          <router-link to="/docs" class="btn btn-xs btn-ghost font-normal hover:text-base-content">开发文档</router-link>
        </div>
      </div>

      <!-- Right: Model Switcher, Theme, and Profile -->
      <div class="flex-none flex items-center gap-2 sm:gap-3">
        <!-- Shared Model Switcher Component -->
        <ModelSwitcher />

        <!-- Theme Controller Dropdown -->
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-sm btn-ghost gap-1 font-normal p-1.5 sm:px-2.5">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
            </svg>
            <span class="capitalize text-xs hidden md:inline">{{ themeStore.currentTheme }}</span>
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
          <div tabindex="0" role="button" class="btn btn-sm btn-ghost gap-2 font-normal pl-1.5 pr-2">
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

    <!-- Main Workspace (Wide & Immersive without Sidebar) -->
    <main class="flex-1 p-4 md:p-6 lg:p-8 max-w-[1700px] w-full mx-auto">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Subtle Footer -->
    <footer class="footer footer-center p-3 border-t border-base-300 text-xs text-base-content/50">
      <div>
        <p>© 2026 JEV 决策模型 API · Liquid AI d1-omni, MiniCPM5-2B & EdgeJev · LFM Architecture</p>
      </div>
    </footer>
  </div>
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

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
