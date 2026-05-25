import type { RouteRecordRaw } from 'vue-router'
import BasicLayout from '@/layouts/BasicLayout.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import PlaceholderView from '@/views/PlaceholderView.vue'

const basicRoutes: RouteRecordRaw[] = [
  {
    path: '/user',
    component: BasicLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: LoginView,
        meta: { title: '用户登录' },
      },
      {
        path: 'register',
        name: 'Register',
        component: RegisterView,
        meta: { title: '用户注册' },
      },
    ],
  },
  {
    path: '/404',
    component: BasicLayout,
    children: [
      {
        path: '',
        name: 'NotFound',
        component: PlaceholderView,
        meta: { title: '页面不存在' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
]

export default basicRoutes