<template>
  <div class="min-h-screen bg-base-100 flex flex-col justify-between relative overflow-hidden select-none">
    <!-- Ambient glowing backdrop circles -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-primary/15 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-accent/15 rounded-full blur-3xl pointer-events-none"></div>

    <!-- Top Navigation / Theme Selector -->
    <header class="w-full max-w-7xl mx-auto p-4 md:p-6 flex items-center justify-between z-10">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-content font-black text-xl shadow-md">
          J
        </div>
        <div>
          <span class="font-bold text-lg tracking-wide bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            JEV 决策中台
          </span>
          <span class="badge badge-outline badge-xs ml-2 font-mono">v1.0.0</span>
        </div>
      </div>

      <!-- Theme Selector Dropdown -->
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-sm btn-ghost gap-2 font-normal">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
          <span class="capitalize text-xs hidden sm:inline">{{ themeStore.currentTheme }}</span>
        </div>
        <ul tabindex="0" class="dropdown-content menu p-2 shadow-xl bg-base-200 rounded-box w-36 z-50 text-xs border border-base-300">
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
    </header>

    <!-- Main Login Card -->
    <main class="flex-1 flex items-center justify-center px-4 py-8 z-10">
      <div class="card w-full max-w-md bg-base-200/90 backdrop-blur-md border border-base-300 shadow-2xl">
        <div class="card-body p-6 sm:p-8 space-y-5">
          <!-- Card Title & Description -->
          <div class="text-center space-y-1.5">
            <h2 class="text-2xl font-black tracking-tight text-base-content">
              管理员登录
            </h2>
            <p class="text-xs text-base-content/70">
              访问 Liquid AI d1-omni-600M 决策引擎中台控制系统
            </p>
          </div>

          <!-- Error Alert Banner -->
          <div v-if="authStore.error" class="alert alert-error text-xs py-2.5 px-3.5 shadow-sm rounded-lg flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="font-medium flex-1">{{ authStore.error }}</span>
          </div>

          <!-- Login Form -->
          <form @submit.prevent="handleLogin" class="space-y-4">
            <!-- Username Input -->
            <div class="form-control">
              <label class="label pb-1.5">
                <span class="label-text text-xs font-semibold text-base-content/80">用户名</span>
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-base-content/40">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  v-model="username"
                  type="text"
                  placeholder="请输入管理员用户名"
                  class="input input-bordered input-sm sm:input-md w-full pl-10 text-sm focus:input-primary transition-all"
                  required
                  autocomplete="username"
                />
              </div>
            </div>

            <!-- Password Input -->
            <div class="form-control">
              <label class="label pb-1.5 flex justify-between">
                <span class="label-text text-xs font-semibold text-base-content/80">密码</span>
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-base-content/40">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入管理员密码"
                  class="input input-bordered input-sm sm:input-md w-full pl-10 pr-10 text-sm focus:input-primary transition-all"
                  required
                  autocomplete="current-password"
                />
                <!-- Show/Hide Toggle -->
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center text-base-content/40 hover:text-base-content/80"
                  @click="showPassword = !showPassword"
                  tabindex="-1"
                >
                  <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              class="btn btn-primary w-full btn-sm sm:btn-md font-bold tracking-wide shadow-md mt-2"
              :disabled="authStore.loading"
            >
              <span v-if="authStore.loading" class="loading loading-spinner loading-sm"></span>
              <span>{{ authStore.loading ? '正在验证身份...' : '登录中台控制台' }}</span>
            </button>
          </form>

          <!-- Divider -->
          <div class="divider my-1 text-xs text-base-content/40">环境配置说明</div>

          <!-- Configuration Hint Box -->
          <div class="bg-base-300/40 rounded-xl p-3.5 border border-base-300 text-xs space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-base-content/80 flex items-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                后端 .env 凭据配置
              </span>
              <button
                type="button"
                class="btn btn-ghost btn-xs text-primary font-medium hover:underline p-0 h-auto"
                @click="fillDefaultCredentials"
              >
                一键填入默认账号
              </button>
            </div>
            <p class="text-[11px] text-base-content/60 leading-relaxed">
              账密已由后端 <code class="font-mono bg-base-300 px-1 py-0.5 rounded text-primary">backend/.env</code> 文件统一管理：
            </p>
            <div class="font-mono text-[11px] bg-base-300/60 p-2 rounded text-base-content/70 space-y-0.5">
              <div>ADMIN_USERNAME=admin</div>
              <div>ADMIN_PASSWORD=admin123</div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="w-full text-center py-4 text-xs text-base-content/50 z-10">
      <p>© 2026 JEV 决策模型 API · Powered by Liquid AI d1-omni-600M</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const username = ref('admin')
const password = ref('')
const showPassword = ref(false)

function fillDefaultCredentials() {
  username.value = 'admin'
  password.value = 'admin123'
}

async function handleLogin() {
  if (!username.value || !password.value) return

  const success = await authStore.login({
    username: username.value,
    password: password.value,
  })

  if (success) {
    const redirectPath = (route.query.redirect as string) || '/'
    router.replace(redirectPath)
  }
}
</script>
