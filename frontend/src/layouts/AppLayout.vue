<template>
  <div class="drawer lg:drawer-open min-h-screen bg-base-100 text-base-content">
    <input id="app-drawer" type="checkbox" class="drawer-toggle" />

    <!-- Page Content Container -->
    <div class="drawer-content flex flex-col min-h-screen">
      <!-- Navbar -->
      <Navbar />

      <!-- Main Router View Area -->
      <main class="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- Footer -->
      <footer class="footer footer-center p-4 border-t border-base-300 text-xs text-base-content/50">
        <div>
          <p>© 2026 JEV 决策模型 API · Powered by Liquid AI d1-omni-600M · LFM Architecture</p>
        </div>
      </footer>
    </div>

    <!-- Drawer Side (Sidebar) -->
    <div class="drawer-side z-40">
      <label for="app-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
      <Sidebar />
    </div>
  </div>
</template>

<script setup lang="ts">
import Navbar from '@/components/Navbar.vue'
import Sidebar from '@/components/Sidebar.vue'
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
