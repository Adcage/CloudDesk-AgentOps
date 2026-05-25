import { createRouter, createWebHistory, type Router, type RouteRecordRaw } from 'vue-router'

const basicModules = import.meta.glob('./basic.ts', { eager: true })
const clouddeskModules = import.meta.glob('./clouddesk.ts', { eager: true })
const adminModules = import.meta.glob('./admin.ts', { eager: true })

function collectRoutes(modules: Record<string, unknown>): RouteRecordRaw[] {
  const routes: RouteRecordRaw[] = []
  Object.entries(modules).forEach(([key, value]) => {
    if (key !== './index.ts') {
      const moduleRoutes = (value as { default?: unknown }).default || value
      if (Array.isArray(moduleRoutes)) {
        routes.push(...moduleRoutes)
      } else {
        routes.push(moduleRoutes as RouteRecordRaw)
      }
    }
  })
  return routes
}

const routeModules: RouteRecordRaw[] = [
  ...collectRoutes(basicModules),
  ...collectRoutes(clouddeskModules),
  ...collectRoutes(adminModules),
]

const router: Router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routeModules,
})

export function initRouterGuards() {
  setupRouterGuards(router)
}

export default router

const WHITE_LIST = ['/user/login', '/user/register', '/404']
let sessionVerified = false

function setupRouterGuards(router: Router) {
  router.beforeEach(async (to, _from, next) => {
    if (to.meta?.title) {
      document.title = `${to.meta.title} - CloudDesk`
    } else {
      document.title = 'CloudDesk'
    }

    if (WHITE_LIST.includes(to.path)) {
      next()
      return
    }

    const { useUserStore } = await import('@/stores/user')
    const userStore = useUserStore()

    if (!sessionVerified) {
      await userStore.fetchCurrentUser()
      sessionVerified = true
    }

    if (!userStore.isLoggedIn) {
      next({ path: '/user/login', query: { redirect: to.fullPath } })
      return
    }

    next()
  })

  router.onError((error) => {
    console.error('路由错误:', error)
  })
}
