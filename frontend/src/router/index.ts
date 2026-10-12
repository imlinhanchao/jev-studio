import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import PlaygroundLayout from '@/layouts/PlaygroundLayout.vue'
import { useAuthStore } from '@/stores/authStore'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '决策中台登录', public: true },
  },
  {
    path: '/playground',
    component: PlaygroundLayout,
    children: [
      {
        path: '',
        name: 'Playground',
        component: () => import('@/views/PlaygroundView.vue'),
        meta: { title: '决策 Studio' },
      },
    ],
  },
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '控制台概览' },
      },
      {
        path: 'api-keys',
        name: 'ApiKeys',
        component: () => import('@/views/KeysView.vue'),
        meta: { title: 'API Key 管理' },
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/AnalyticsView.vue'),
        meta: { title: 'Token 消耗统计' },
      },
      {
        path: 'docs',
        name: 'Docs',
        component: () => import('@/views/DocsView.vue'),
        meta: { title: '开发者文档' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} | JEV 决策中台 (Liquid AI d1-omni)`
  }

  const authStore = useAuthStore()
  const isPublic = to.meta.public === true

  if (!authStore.isAuthenticated && !isPublic) {
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
    return
  }

  if (authStore.isAuthenticated && to.path === '/login') {
    next('/')
    return
  }

  next()
})

export default router
