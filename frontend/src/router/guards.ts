import type { Router } from 'vue-router'
import { useUserStore } from '@/stores/user'

const WHITE_LIST = ['/user/login', '/user/register', '/404']

export function setupRouterGuards(router: Router): void {
  router.beforeEach(async (to, _from, next) => {
    if (to.meta?.title) {
      document.title = `${to.meta.title} - CloudDesk`
    } else {
      document.title = 'CloudDesk'
    }

    const userStore = useUserStore()

    if (WHITE_LIST.includes(to.path)) {
      next()
      return
    }

    if (!userStore.isLoggedIn) {
      await userStore.fetchCurrentUser()
    }

    if (!userStore.isLoggedIn) {
      next({ path: '/user/login', query: { redirect: to.fullPath } })
      return
    }

    next()
  })

  router.afterEach((_to, _from) => {})

  router.onError((error) => {
    console.error('路由错误:', error)
  })
}
